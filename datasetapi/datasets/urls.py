from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet, SummaryStatisticsViewSet, DatasetColumnViewSet
from .summary_views import dataset_summary_list, data_summary_api
from .equipment_views import (
    equipment_csv_upload, data_summary, validate_csv, equipment_data_preview
)
from .auth_views import (
    register_user, login_user, logout_user, user_profile, auth_status,
    CustomTokenObtainPairView, CustomTokenRefreshView
)
from .pdf_views import (
    generate_pdf_report, preview_pdf_report, list_available_reports, batch_generate_reports
)
from .history_views import (
    history_status, manual_cleanup, cleanup_preview, dataset_history,
    delete_specific_dataset, history_settings
)
from .api_root_views import api_root, home_redirect

# Create router and register viewsets
router = DefaultRouter()
router.register(r'datasets', DatasetViewSet)
router.register(r'statistics', SummaryStatisticsViewSet)
router.register(r'columns', DatasetColumnViewSet)

urlpatterns = [
    # Root endpoints
    path('', home_redirect, name='home'),
    path('api/', api_root, name='api-root'),
    
    # Data Summary API endpoints (NEW) - MOVED TO TOP FOR PRIORITY
    path('api/data-summary/<int:dataset_id>/', data_summary_api, name='data-summary-api'),
    path('api/data-summaries/', dataset_summary_list, name='dataset-summary-list'),
    
    # DRF router URLs
    path('api/', include(router.urls)),
    
    # Authentication endpoints
    path('api/auth/register/', register_user, name='auth-register'),
    path('api/auth/login/', login_user, name='auth-login'),
    path('api/auth/logout/', logout_user, name='auth-logout'),
    path('api/auth/profile/', user_profile, name='auth-profile'),
    path('api/auth/status/', auth_status, name='auth-status'),
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    
    # Equipment-specific endpoints
    path('api/equipment/upload/', equipment_csv_upload, name='equipment-csv-upload'),
    path('api/equipment/summary/', data_summary, name='data-summary-all'),
    path('api/equipment/summary/<int:dataset_id>/', data_summary, name='data-summary-specific'),
    path('api/equipment/validate/', validate_csv, name='validate-csv'),
    path('api/equipment/preview/<int:dataset_id>/', equipment_data_preview, name='equipment-data-preview'),
    
    # PDF report endpoints
    path('api/reports/pdf/<int:dataset_id>/', generate_pdf_report, name='generate-pdf-report'),
    path('api/reports/preview/<int:dataset_id>/', preview_pdf_report, name='preview-pdf-report'),
    path('api/reports/available/', list_available_reports, name='list-available-reports'),
    path('api/reports/batch/', batch_generate_reports, name='batch-generate-reports'),
    
    # History management endpoints
    path('api/history/status/', history_status, name='history-status'),
    path('api/history/cleanup/', manual_cleanup, name='manual-cleanup'),
    path('api/history/cleanup-preview/', cleanup_preview, name='cleanup-preview'),
    path('api/history/datasets/', dataset_history, name='dataset-history'),
    path('api/history/datasets/<int:dataset_id>/', delete_specific_dataset, name='delete-specific-dataset'),
    path('api/history/settings/', history_settings, name='history-settings'),
]