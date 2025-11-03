"""
Sample Knowledge Base Articles
This script populates the KB with common support articles
"""

# Sample KB articles covering common support scenarios
SAMPLE_ARTICLES = [
    {
        "article_id": "kb_001_shipping_policy",
        "title": "Shipping Policy and Delivery Times",
        "category": "shipping",
        "content": """
        Standard Shipping Times:
        - Domestic orders: 5-7 business days
        - Express shipping: 2-3 business days
        - International: 10-15 business days
        
        Order Processing:
        - Orders are processed within 1-2 business days
        - You'll receive a tracking number via email once shipped
        - Track your order at: https://tracking.example.com
        
        Shipping Delays:
        If your order hasn't arrived within the expected timeframe:
        1. Check your tracking number for updates
        2. Contact us with your order number
        3. We'll investigate and provide an update within 24 hours
        
        Holiday Shipping:
        During peak seasons (Black Friday, Christmas), please allow 2-3 extra days for processing.
        """
    },
    {
        "article_id": "kb_002_refund_policy",
        "title": "Refund and Return Policy",
        "category": "refund",
        "content": """
        Return Window:
        - 30 days from delivery date for full refund
        - 60 days for store credit
        
        Eligible Items:
        - Unused items in original packaging
        - Items with tags still attached
        - Non-personalized products
        
        Non-Returnable Items:
        - Final sale items
        - Opened software or digital products
        - Personalized or custom items
        
        Return Process:
        1. Contact support with your order number
        2. We'll email you a prepaid return label
        3. Ship the item back within 14 days
        4. Refund processed within 5-7 business days after receipt
        
        Refund Method:
        - Refunds are issued to the original payment method
        - Shipping costs are non-refundable (unless item was defective)
        """
    },
    {
        "article_id": "kb_003_damaged_items",
        "title": "Damaged or Defective Products",
        "category": "product",
        "content": """
        If you received a damaged or defective item, we apologize!
        
        What to Do:
        1. Take photos of the damage (item and packaging)
        2. Contact us within 7 days of delivery
        3. Provide your order number and photos
        
        Resolution Options:
        - Free replacement (shipped immediately)
        - Full refund (no need to return damaged item)
        - Partial refund if you want to keep it
        
        Shipping Damage:
        If the box arrived damaged, note it when accepting delivery and take photos.
        This helps us file claims with the carrier.
        
        Processing Time:
        - Replacements ship within 1 business day
        - Refunds process within 2-3 business days
        """
    },
    {
        "article_id": "kb_004_account_access",
        "title": "Account Login and Password Reset",
        "category": "account",
        "content": """
        Can't Log In?
        
        Password Reset:
        1. Go to the login page
        2. Click "Forgot Password"
        3. Enter your email address
        4. Check your email for reset link (check spam folder)
        5. Link expires in 24 hours
        
        Still Can't Log In?
        - Make sure you're using the correct email
        - Clear browser cookies and cache
        - Try a different browser
        - Check if Caps Lock is on
        
        Account Locked:
        After 5 failed login attempts, your account locks for 30 minutes.
        Wait or contact support to unlock immediately.
        
        Email Not Received:
        - Check spam/junk folder
        - Add noreply@example.com to contacts
        - Wait 10 minutes (sometimes delayed)
        - Contact support if still not received
        """
    },
    {
        "article_id": "kb_005_billing_issues",
        "title": "Billing and Payment Problems",
        "category": "billing",
        "content": """
        Common Billing Issues:
        
        Duplicate Charges:
        - Sometimes a charge appears twice temporarily
        - One is usually a pre-authorization that drops off in 3-5 days
        - If both charges post, contact us immediately for refund
        
        Payment Declined:
        - Verify card details (number, CVV, expiration)
        - Check with your bank (insufficient funds, fraud hold)
        - Try a different payment method
        - Ensure billing address matches card
        
        Subscription Charges:
        - Subscriptions renew automatically
        - Charges occur on the same day each month
        - Cancel anytime before next billing date
        - Refunds available within 48 hours of charge
        
        Unrecognized Charges:
        Check your statement for:
        - "EXAMPLE.COM" or "EXAMPLE STORE" (our billing names)
        - Contact us with the charge date and amount
        - We'll investigate within 24 hours
        """
    },
    {
        "article_id": "kb_006_order_tracking",
        "title": "How to Track Your Order",
        "category": "shipping",
        "content": """
        Tracking Your Order:
        
        Getting Your Tracking Number:
        - Sent via email within 24 hours of order
        - Check spam folder if not received
        - Also available in your account under "Orders"
        
        Tracking Shows "Processing":
        - Label created but not yet picked up by carrier
        - Usually updates within 24-48 hours
        - Normal during first 2 days after order
        
        No Tracking Updates:
        - Carrier may not scan at every checkpoint
        - Common for ground shipping
        - Updates typically show at origin, in transit, and delivery
        
        Track Your Package:
        1. Copy tracking number from email
        2. Visit carrier website (USPS, UPS, FedEx)
        3. Or use our tracking page: tracking.example.com
        
        Tracking Says Delivered But Not Received:
        - Check with neighbors
        - Look around delivery location (porch, mailbox)
        - Wait 24 hours (sometimes marked delivered early)
        - Contact carrier first, then us if still missing
        """
    },
    {
        "article_id": "kb_007_cancel_order",
        "title": "How to Cancel or Modify an Order",
        "category": "general",
        "content": """
        Order Cancellation:
        
        Before Shipment:
        - Contact us ASAP with order number
        - Orders can be cancelled within 24 hours
        - Full refund issued immediately
        
        After Shipment:
        - Cannot cancel once shipped
        - Refuse delivery and it will return to us
        - Or accept delivery and start a return
        
        Modify Order Details:
        Before shipping, you can change:
        - Shipping address
        - Shipping speed
        - Payment method
        
        Cannot modify:
        - Items in the order (must cancel and reorder)
        - Order once it's shipped
        
        How to Request:
        1. Email support@example.com with order number
        2. Or use live chat (9am-6pm EST)
        3. Specify what you need changed
        
        Processing Time:
        - Modifications: Within 2 hours during business hours
        - Cancellations: Immediate confirmation
        """
    },
    {
        "article_id": "kb_008_product_warranty",
        "title": "Product Warranty and Technical Support",
        "category": "technical",
        "content": """
        Warranty Coverage:
        
        Standard Warranty:
        - 1 year from purchase date
        - Covers manufacturing defects
        - Does not cover normal wear, accidents, or misuse
        
        Extended Warranty:
        - Available for purchase up to 30 days after order
        - Extends coverage to 3 years
        - Includes accidental damage protection
        
        Technical Support:
        - Free lifetime technical support
        - Available via email, chat, or phone
        - Average response time: 4 hours
        
        Warranty Claims:
        1. Contact support with order number
        2. Describe the issue and troubleshooting tried
        3. Provide photos if applicable
        4. We'll provide troubleshooting or replacement
        
        Replacement Process:
        - Approved claims ship replacement within 2 days
        - Return defective item with prepaid label
        - No charge for warranty replacements
        """
    },
    {
        "article_id": "kb_009_international_orders",
        "title": "International Shipping and Customs",
        "category": "shipping",
        "content": """
        International Shipping:
        
        Delivery Times:
        - Canada: 7-10 business days
        - Europe: 10-15 business days
        - Asia/Pacific: 12-18 business days
        - Other regions: 15-25 business days
        
        Customs and Duties:
        - Customer responsible for import duties/taxes
        - Varies by country
        - Paid to carrier upon delivery
        - We mark accurate value on customs forms
        
        Tracking:
        - International tracking may have delays
        - Stops updating during customs clearance
        - Updates resume once cleared
        
        Customs Delays:
        - Can add 3-7 days to delivery
        - Contact local customs office for status
        - We cannot expedite customs clearance
        
        Address Requirements:
        - Include phone number (required for customs)
        - Use English characters
        - Include postal code
        - Specify province/state if applicable
        """
    },
    {
        "article_id": "kb_010_subscription_management",
        "title": "Managing Your Subscription",
        "category": "billing",
        "content": """
        Subscription Options:
        
        Monthly Plan:
        - $49.99/month
        - Cancel anytime
        - Billed on same date each month
        
        Annual Plan:
        - $499/year (save $100)
        - Billed once per year
        - 30-day money back guarantee
        
        How to Cancel:
        1. Log into your account
        2. Go to Settings > Subscription
        3. Click "Cancel Subscription"
        4. Confirm cancellation
        
        Cancellation Policy:
        - Access continues until end of billing period
        - No partial refunds (except within first 30 days)
        - Can reactivate anytime
        
        Pause Subscription:
        - Available for 1-3 months
        - No charge during pause
        - Automatically resumes after pause period
        
        Change Plan:
        - Upgrade: Takes effect immediately, prorated charge
        - Downgrade: Takes effect next billing cycle
        """
    }
]


def load_sample_articles():
    """Load sample articles into the knowledge base"""
    import sys
    import os
    
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from services.kb_service import get_kb_service
    
    kb = get_kb_service()
    
    print("\n" + "="*70)
    print("  📚 Loading Sample Knowledge Base Articles")
    print("="*70 + "\n")
    
    # Add all articles
    added = kb.add_articles_bulk(SAMPLE_ARTICLES)
    
    print(f"\n✅ Successfully loaded {added} articles!")
    
    # Show stats
    stats = kb.get_stats()
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"   Total articles: {stats['total_articles']}")
    print(f"   Categories:")
    for category, count in stats['categories'].items():
        print(f"      - {category}: {count}")
    
    print("\n" + "="*70 + "\n")
    
    return added


if __name__ == "__main__":
    load_sample_articles()
