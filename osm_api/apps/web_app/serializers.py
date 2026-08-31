from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import (
    BoundaryPolygonLvl2, BoundaryPolygonLvl4, BoundaryPolygonLvl6, BoundaryPolygonLvl8,
    BuildingPolygon, HighwayLine, LandusePolygon, ParkingPolygon,
    PoiPoint, PoiPolygon, RailwayLine,
    SettlementPoint, SettlementPolygon,
    VegetationPolygon, WaterLine, WaterPolygon,
)


class BoundaryPolygonLvl2Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl2
        geo_field = 'geom'
        fields = '__all__'


class BoundaryPolygonLvl4Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl4
        geo_field = 'geom'
        fields = '__all__'


class BoundaryPolygonLvl6Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl6
        geo_field = 'geom'
        fields = '__all__'


class BoundaryPolygonLvl8Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = BoundaryPolygonLvl8
        geo_field = 'geom'
        fields = '__all__'


class BuildingPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = BuildingPolygon
        geo_field = 'geom'
        fields = '__all__'


class HighwayLineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = HighwayLine
        geo_field = 'geom'
        fields = '__all__'


class LandusePolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = LandusePolygon
        geo_field = 'geom'
        fields = '__all__'


class ParkingPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ParkingPolygon
        geo_field = 'geom'
        fields = '__all__'


class PoiPointSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PoiPoint
        geo_field = 'geom'
        fields = '__all__'


class PoiPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PoiPolygon
        geo_field = 'geom'
        fields = '__all__'


class RailwayLineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RailwayLine
        geo_field = 'geom'
        fields = '__all__'


class SettlementPointSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SettlementPoint
        geo_field = 'geom'
        fields = '__all__'


class SettlementPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SettlementPolygon
        geo_field = 'geom'
        fields = '__all__'


class VegetationPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = VegetationPolygon
        geo_field = 'geom'
        fields = '__all__'


class WaterLineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = WaterLine
        geo_field = 'geom'
        fields = '__all__'


class WaterPolygonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = WaterPolygon
        geo_field = 'geom'
        fields = '__all__'
