"""
Authentication API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import datetime

from ..models.user import (
    User,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
    UserRole,
)
from ..services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_user_id,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# In-memory user storage (replace with database in production)
users_db = {}


# Initialize with demo users
def init_demo_users():
    """Create demo users for testing"""
    demo_users = [
        {
            "email": "admin@tixly.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
        },
        {
            "email": "manager@tixly.com",
            "password": "manager123",
            "full_name": "Manager Sarah",
            "role": UserRole.MANAGER,
        },
        {
            "email": "agent@tixly.com",
            "password": "agent123",
            "full_name": "Agent John",
            "role": UserRole.AGENT,
            "agent_skills": ["billing", "technical"],
            "team": "support",
        },
        {
            "email": "customer@example.com",
            "password": "customer123",
            "full_name": "Customer Jane",
            "role": UserRole.CUSTOMER,
        },
    ]

    for demo_user in demo_users:
        user_id = generate_user_id()
        password = demo_user.pop("password")

        user = User(
            user_id=user_id,
            **demo_user,  # unpacks the user dictionary.
            hashed_password=hash_password(password),
            created_at=datetime.utcnow(),
        )
        users_db[user.email] = user
        print(f"✅ Created demo user: {user.email} (password: {password})")


# Initialize demo users on module load
init_demo_users()


# ==================== DEPENDENCY FUNCTIONS ====================


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("email")
    if email is None:
        raise credentials_exception

    user = users_db.get(email)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (alias for get_current_user)"""
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency factory for role-based access control

    Usage:
        @router.get("/admin-only")
        async def admin_route(
            current_user: User = Depends(require_role([UserRole.ADMIN]))
        ):
            return {"message": "Admin access granted"}
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker


# ==================== API ENDPOINTS ====================


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate):
    """
    Register a new user

    - Checks if email already exists
    - Hashes password
    - Creates user record
    - Returns user info (no password)
    """
    # Check if user already exists
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    user_id = generate_user_id()
    user = User(
        user_id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=hash_password(user_data.password),
        created_at=datetime.utcnow(),
        is_active=True,
    )

    # Store user
    users_db[user.email] = user

    print(f"✅ New user registered: {user.email} ({user.role.value})")

    # Return user without password
    return UserResponse(**user.dict())


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email and password

    OAuth2 compatible token endpoint:
    - Accepts form data (username=email, password)
    - Returns JWT access token
    - Includes user info in response
    """
    # Find user by email (OAuth2 uses 'username' field)
    user = users_db.get(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()

    # Create access token
    access_token = create_access_token(
        data={"user_id": user.user_id, "email": user.email, "role": user.role.value}
    )

    print(f"✅ User logged in: {user.email} ({user.role.value})")

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=UserResponse(**user.dict()),
    )


@router.post("/login/json", response_model=Token)
async def login_json(credentials: UserLogin):
    """
    Alternative login endpoint that accepts JSON instead of form data

    Easier to use from frontend applications
    """
    # Find user
    user = users_db.get(credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()

    # Create access token
    access_token = create_access_token(
        data={"user_id": user.user_id, "email": user.email, "role": user.role.value}
    )

    print(f"✅ User logged in: {user.email} ({user.role.value})")

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(**user.dict()),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information

    Requires valid JWT token in Authorization header:
    Authorization: Bearer <token>
    """
    return UserResponse(**current_user.dict())


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """
    List all users (admin/manager only)

    Protected endpoint - requires ADMIN or MANAGER role
    """
    return [UserResponse(**user.dict()) for user in users_db.values()]
