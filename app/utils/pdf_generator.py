from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from typing import List

def generate_bill_pdf(order, settings):
    """
    Generate a PDF bill for a single order

    Args:
        order: The order object with all details
        settings: The hotel settings object

    Returns:
        BytesIO: A buffer containing the PDF data
    """
    # Convert single order to list and use the multi-order function
    return generate_multi_order_bill_pdf([order], settings)

def generate_multi_order_bill_pdf(orders: List, settings):
    """
    Generate a PDF bill for multiple orders in a receipt-like format

    Args:
        orders: List of order objects with all details
        settings: The hotel settings object

    Returns:
        BytesIO: A buffer containing the PDF data
    """
    buffer = BytesIO()
    # Use a narrower page size to mimic a receipt
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(4*inch, 11*inch),  # Typical receipt width
        rightMargin=10,
        leftMargin=10,
        topMargin=10,
        bottomMargin=10
    )

    # Create styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='HotelName',
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1,  # Center alignment
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='HotelTagline',
        fontName='Helvetica',
        fontSize=9,
        alignment=1,  # Center alignment
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='HotelAddress',
        fontName='Helvetica',
        fontSize=8,
        alignment=1,  # Center alignment
        spaceAfter=1
    ))
    styles.add(ParagraphStyle(
        name='BillInfo',
        fontName='Helvetica',
        fontSize=8,
        alignment=0,  # Left alignment
        spaceAfter=1
    ))
    styles.add(ParagraphStyle(
        name='BillInfoRight',
        fontName='Helvetica',
        fontSize=8,
        alignment=2,  # Right alignment
        spaceAfter=1
    ))
    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        name='ItemName',
        fontName='Helvetica',
        fontSize=8,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        name='ItemValue',
        fontName='Helvetica',
        fontSize=8,
        alignment=2  # Right alignment
    ))
    styles.add(ParagraphStyle(
        name='Total',
        fontName='Helvetica-Bold',
        fontSize=9,
        alignment=1  # Center alignment
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontName='Helvetica',
        fontSize=7,
        alignment=1,  # Center alignment
        textColor=colors.black
    ))

    # Create content elements
    elements = []

    # We're not using the logo in this receipt-style bill
    # Add hotel name and info
    elements.append(Paragraph(settings.hotel_name.upper(), styles['HotelName']))

    # Add tagline (if any, otherwise use a default)
    tagline = "AN AUTHENTIC CUISINE SINCE 2000"
    elements.append(Paragraph(tagline, styles['HotelTagline']))

    # Add address with formatting similar to the image
    if settings.address:
        elements.append(Paragraph(settings.address, styles['HotelAddress']))

    # Add contact info
    if settings.contact_number:
        elements.append(Paragraph(f"Contact: {settings.contact_number}", styles['HotelAddress']))

    # Add tax ID (GSTIN)
    if settings.tax_id:
        elements.append(Paragraph(f"GSTIN: {settings.tax_id}", styles['HotelAddress']))

    # Add a separator line
    elements.append(Paragraph("_" * 50, styles['HotelAddress']))

    # Add bill details in a more receipt-like format
    # Use the first order for common details
    first_order = orders[0]

    # Create a table for the bill header info
    # Get customer name if available
    customer_name = ""
    if hasattr(first_order, 'person_name') and first_order.person_name:
        customer_name = first_order.person_name

    bill_info_data = [
        ["Name:", customer_name],
        [f"Date: {datetime.now().strftime('%d/%m/%y')}", f"Dine In: {first_order.table_number}"],
        [f"{datetime.now().strftime('%H:%M')}", f"Bill No.: {first_order.id}"]
    ]

    bill_info_table = Table(bill_info_data, colWidths=[doc.width/2-20, doc.width/2-20])
    bill_info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (1, 0), 0.5, colors.black),
    ]))

    elements.append(bill_info_table)
    elements.append(Paragraph("_" * 50, styles['HotelAddress']))

    # Create header for items table
    items_header = [["Item", "Qty.", "Price", "Amount"]]
    items_header_table = Table(items_header, colWidths=[doc.width*0.4, doc.width*0.15, doc.width*0.2, doc.width*0.25])
    items_header_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 8),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
    ]))

    elements.append(items_header_table)

    # Add all order items
    total_items = 0
    grand_total = 0

    for order in orders:
        order_data = []

        for item in order.items:
            dish_name = item.dish.name if item.dish else "Unknown Dish"
            price = item.dish.price if item.dish else 0
            quantity = item.quantity
            total = price * quantity
            grand_total += total
            total_items += quantity

            order_data.append([
                dish_name,
                str(quantity),
                f"{price:.2f}",
                f"{total:.2f}"
            ])

        # Create the table for this order's items
        if order_data:
            items_table = Table(order_data, colWidths=[doc.width*0.4, doc.width*0.15, doc.width*0.2, doc.width*0.25])
            items_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ]))

            elements.append(items_table)

    # Add a separator line
    elements.append(Paragraph("_" * 50, styles['HotelAddress']))

    # Add totals section
    # Calculate tax (assuming 5% CGST and 5% SGST like in the image)
    tax_rate = 0.05  # 5%
    cgst = grand_total * tax_rate
    sgst = grand_total * tax_rate
    subtotal = grand_total - cgst - sgst

    totals_data = [
        [f"Total Qty: {total_items}", f"Sub Total", f"{subtotal:.2f}"],
        ["", f"CGST", f"{cgst:.2f}"],
        ["", f"SGST", f"{sgst:.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[doc.width*0.4, doc.width*0.35, doc.width*0.25])
    totals_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ]))

    elements.append(totals_table)

    # Add grand total with emphasis
    elements.append(Paragraph("_" * 50, styles['HotelAddress']))
    elements.append(Paragraph(f"Grand Total    ₹{grand_total:.2f}", styles['Total']))
    elements.append(Paragraph("_" * 50, styles['HotelAddress']))

    # Add license info and thank you message
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("FSSAI Lic No: 12018033000205", styles['Footer']))
    elements.append(Paragraph("!!! Thank You !!! Visit Again !!!", styles['Footer']))

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)

    return buffer
