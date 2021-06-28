from django.urls import path
from . import views
from webcrawlUI.helpers.qgram_index import QGramIndex

urlpatterns = [
    path('', views.home, name="home"),
    path('runWebCrawlTask/<str:state_name>/<str:city_name>/', views.run_web_crawl_task, name="runWebCrawlTask"),
    path('runGoogleSpider/<str:state_name>/<str:city_name>/', views.run_google_spider, name="runGoogleSpider"),
    path('genereateCitiesSpider/<int:id>/', views.generate_cities_spider, name="genereateCitiesSpider"),
    path('search/<str:values>/', views.searchCities),
    path('renderCity/<str:city>/', views.renderCity),
    path('<str:name>/', views.cities),
    path('<str:state_name>/<str:city_name>/', views.city)
]
obj = QGramIndex(3)
obj.build()