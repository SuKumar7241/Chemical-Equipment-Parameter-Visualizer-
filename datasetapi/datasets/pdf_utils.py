"""
PDF report generation utilities using ReportLab
Generates comprehensive PDF summaries for datasets
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
from django.utils import timezone
from io import BytesIO
import os
import logging

logger = logging.getLogger(__name__)


class DatasetPDFGenerator:
    """
    PDF generator for dataset analysis reports
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkgreen
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkred
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='MetricStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20
        ))
    
    def generate_dataset_report(self, dataset, output_path=None):
        """
        Generate a comprehensive PDF report for a dataset
        
        Args:
            dataset: Dataset instance
            output_path: Optional path to save the PDF
            
        Returns:
            BytesIO buffer containing the PDF data
        """
        try:
            # Create PDF buffer
            buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the story (content)
            story = []
            
            # Add title page
            self._add_title_page(story, dataset)
            
            # Add dataset overview
            self._add_dataset_overview(story, dataset)
            
            # Add operational metrics (if available)
            if hasattr(dataset, 'summary'):
                self._add_operational_metrics(story, dataset.summary)
                
                # Add equipment analysis
                self._add_equipment_analysis(story, dataset.summary)
                
                # Add data quality metrics
                self._add_data_quality_metrics(story, dataset.summary)
                
                # Add column analysis
                self._add_column_analysis(story, dataset)
            
            # Add footer information
            self._add_footer_info(story, dataset)
            
            # Build PDF
            doc.build(story)
            
            # Save to file if path provided
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise e
    
    def _add_title_page(self, story, dataset):
        """Add title page to the PDF"""
        # Main title
        title = Paragraph("Dataset Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Dataset name
        dataset_title = Paragraph(f"<b>{dataset.name}</b>", self.styles['CustomSubtitle'])
        story.append(dataset_title)
        story.append(Spacer(1, 10))
        
        # Description
        if dataset.description:
            desc = Paragraph(f"<i>{dataset.description}</i>", self.styles['Normal'])
            story.append(desc)
            story.append(Spacer(1, 20))
        
        # Basic info table
        basic_info_data = [
            ['File Name', dataset.file_name],
            ['File Type', dataset.file_type.upper()],
            ['Upload Date', dataset.upload_date.strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Rows', f"{dataset.total_rows:,}" if dataset.total_rows else 'N/A'],
            ['Total Columns', str(dataset.total_columns) if dataset.total_columns else 'N/A'],
            ['File Size', f"{dataset.file_size:,} bytes" if dataset.file_size else 'N/A'],
            ['Processing Status', 'Processed' if dataset.is_processed else 'Not Processed']
        ]
        
        basic_info_table = Table(basic_info_data, colWidths=[2*inch, 3*inch])
        basic_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(basic_info_table)
        story.append(PageBreak())
    
    def _add_dataset_overview(self, story, dataset):
        """Add dataset overview section"""
        story.append(Paragraph("Dataset Overview", self.styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.darkred))
        story.append(Spacer(1, 10))
        
        # Column information
        if dataset.column_names:
            story.append(Paragraph("Columns:", self.styles['Heading3']))
            
            column_data = [['#', 'Column Name', 'Data Type']]
            for i, col_name in enumerate(dataset.column_names, 1):
                col_type = dataset.column_types.get(col_name, 'Unknown') if dataset.column_types else 'Unknown'
                column_data.append([str(i), col_name, col_type])
            
            column_table = Table(column_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch])
            column_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(column_table)
            story.append(Spacer(1, 20))
    
    def _add_operational_metrics(self, story, summary):
        """Add operational metrics section"""
        story.append(Paragraph("Operational Metrics", self.styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.darkred))
        story.append(Spacer(1, 10))
        
        # Quick metrics
        metrics_data = [['Metric', 'Value']]
        
        if summary.total_records:
            metrics_data.append(['Total Records', f"{summary.total_records:,}"])
        
        if summary.avg_flowrate is not None:
            metrics_data.append(['Average Flowrate', f"{summary.avg_flowrate:.2f}"])
        
        if summary.avg_pressure is not None:
            metrics_data.append(['Average Pressure', f"{summary.avg_pressure:.2f}"])
        
        if summary.avg_temperature is not None:
            metrics_data.append(['Average Temperature', f"{summary.avg_temperature:.2f}"])
        
        if summary.missing_values_count is not None:
            metrics_data.append(['Missing Values', f"{summary.missing_values_count:,}"])
        
        if len(metrics_data) > 1:  # If we have data beyond headers
            metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        # Detailed operational metrics from statistics_data
        if hasattr(summary, 'statistics_data') and summary.statistics_data:
            operational_metrics = summary.statistics_data.get('operational_metrics', {})
            
            if operational_metrics:
                story.append(Paragraph("Detailed Operational Analysis:", self.styles['Heading3']))
                
                for metric_name, metric_data in operational_metrics.items():
                    if isinstance(metric_data, dict):
                        story.append(Paragraph(f"<b>{metric_name.title()}:</b>", self.styles['MetricStyle']))
                        
                        metric_details = []
                        for key, value in metric_data.items():
                            if value is not None:
                                if isinstance(value, float):
                                    metric_details.append(f"  • {key.replace('_', ' ').title()}: {value:.2f}")
                                else:
                                    metric_details.append(f"  • {key.replace('_', ' ').title()}: {value}")
                        
                        if metric_details:
                            for detail in metric_details:
                                story.append(Paragraph(detail, self.styles['Normal']))
                        
                        story.append(Spacer(1, 10))
    
    def _add_equipment_analysis(self, story, summary):
        """Add equipment analysis section"""
        if not summary.equipment_type_distribution:
            return
        
        story.append(Paragraph("Equipment Analysis", self.styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.darkred))
        story.append(Spacer(1, 10))
        
        # Equipment distribution table
        equipment_data = [['Equipment Type', 'Count', 'Percentage']]
        total_equipment = sum(summary.equipment_type_distribution.values())
        
        for eq_type, count in summary.equipment_type_distribution.items():
            percentage = (count / total_equipment * 100) if total_equipment > 0 else 0
            equipment_data.append([eq_type, str(count), f"{percentage:.1f}%"])
        
        equipment_table = Table(equipment_data, colWidths=[2*inch, 1*inch, 1*inch])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(equipment_table)
        story.append(Spacer(1, 20))
    
    def _add_data_quality_metrics(self, story, summary):
        """Add data quality metrics section"""
        if not hasattr(summary, 'statistics_data') or not summary.statistics_data:
            return
        
        data_quality = summary.statistics_data.get('data_quality', {})
        if not data_quality:
            return
        
        story.append(Paragraph("Data Quality Assessment", self.styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.darkred))
        story.append(Spacer(1, 10))
        
        # Data quality table
        quality_data = [['Quality Metric', 'Value']]
        
        if 'total_rows' in data_quality:
            quality_data.append(['Total Rows', f"{data_quality['total_rows']:,}"])
        
        if 'complete_rows' in data_quality:
            quality_data.append(['Complete Rows', f"{data_quality['complete_rows']:,}"])
        
        if 'missing_data_percentage' in data_quality:
            quality_data.append(['Missing Data %', f"{data_quality['missing_data_percentage']:.2f}%"])
        
        if 'columns_with_missing_data' in data_quality:
            missing_cols = data_quality['columns_with_missing_data']
            quality_data.append(['Columns with Missing Data', str(len(missing_cols))])
        
        quality_table = Table(quality_data, colWidths=[2.5*inch, 2*inch])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(quality_table)
        story.append(Spacer(1, 20))
    
    def _add_column_analysis(self, story, dataset):
        """Add detailed column analysis"""
        columns = dataset.columns.all().order_by('position')
        if not columns:
            return
        
        story.append(Paragraph("Column Analysis", self.styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.darkred))
        story.append(Spacer(1, 10))
        
        # Column details table
        column_data = [['Column', 'Type', 'Non-Null', 'Unique', 'Statistics']]
        
        for col in columns:
            stats_info = []
            
            if col.is_numeric:
                if col.mean_value is not None:
                    stats_info.append(f"Mean: {col.mean_value:.2f}")
                if col.min_value is not None and col.max_value is not None:
                    stats_info.append(f"Range: {col.min_value:.2f} - {col.max_value:.2f}")
            elif col.is_categorical:
                if col.most_frequent_value:
                    stats_info.append(f"Most frequent: {col.most_frequent_value}")
                if col.most_frequent_count:
                    stats_info.append(f"Count: {col.most_frequent_count}")
            
            stats_text = "; ".join(stats_info) if stats_info else "N/A"
            
            column_data.append([
                col.name,
                col.data_type,
                str(col.non_null_count),
                str(col.unique_count),
                stats_text
            ])
        
        column_table = Table(column_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 0.8*inch, 2.4*inch])
        column_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkslategray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(column_table)
        story.append(Spacer(1, 20))
    
    def _add_footer_info(self, story, dataset):
        """Add footer information"""
        story.append(PageBreak())
        story.append(Paragraph("Report Information", self.styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.darkred))
        story.append(Spacer(1, 10))
        
        footer_info = [
            f"Report generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Dataset ID: {dataset.id}",
            f"Analysis performed using Django Dataset Analysis API",
            f"This report reflects the computed summaries and statistics for the uploaded dataset."
        ]
        
        for info in footer_info:
            story.append(Paragraph(info, self.styles['Normal']))
            story.append(Spacer(1, 6))


def generate_dataset_pdf_report(dataset, filename=None):
    """
    Convenience function to generate a PDF report for a dataset
    
    Args:
        dataset: Dataset instance
        filename: Optional filename for the PDF
        
    Returns:
        Tuple of (BytesIO buffer, filename)
    """
    try:
        generator = DatasetPDFGenerator()
        
        # Generate filename if not provided
        if not filename:
            safe_name = "".join(c for c in dataset.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"dataset_report_{safe_name}_{dataset.id}.pdf"
        
        # Generate PDF
        pdf_buffer = generator.generate_dataset_report(dataset)
        
        return pdf_buffer, filename
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise e