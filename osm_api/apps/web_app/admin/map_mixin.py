from django.utils.safestring import mark_safe


class GeoMapMixin:
    readonly_fields = ('map_preview',)

    def map_preview(self, obj):
        geometry = getattr(obj, 'geom', None)  # noqa: model field, not this method
        if not geometry:
            return mark_safe('<span style="color:#6b7280;font-style:italic">—</span>')

        centroid = geometry.centroid
        pk = obj.pk or 'new'
        geojson = geometry.geojson

        html = f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
  #geomap-{pk} {{ height:480px;width:100%;border-radius:10px;overflow:hidden;
    box-shadow:0 4px 24px rgba(0,0,0,0.5);border:1px solid #374151;margin-top:4px; }}
  #geomap-{pk} .leaflet-control-attribution {{
    background:rgba(0,0,0,0.5)!important;color:#9ca3af;font-size:10px;
  }}
</style>
<div id="geomap-{pk}"></div>
<script>
(function(){{
  var gj={geojson};
  var lat={centroid.y},lng={centroid.x};
  function init(){{
    var m=L.map('geomap-{pk}',{{zoomControl:true,attributionControl:true}}).setView([lat,lng],13);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{
      attribution:'\\u00a9 <a href="https://osm.org">OSM</a> \\u00a9 <a href="https://carto.com">CARTO</a>',
      subdomains:'abcd',
      maxZoom:20,
      maxNativeZoom:18
    }}).addTo(m);
    var layer=L.geoJSON(gj,{{
      style:{{color:'#f97316',weight:2.5,fillColor:'#f97316',fillOpacity:0.2}},
      pointToLayer:function(f,ll){{
        return L.circleMarker(ll,{{
          radius:9,color:'#ea580c',weight:2.5,
          fillColor:'#fb923c',fillOpacity:1
        }});
      }}
    }}).addTo(m);
    try{{m.fitBounds(layer.getBounds(),{{padding:[50,50]}});}}catch(e){{m.setView([lat,lng],14);}}
  }}
  if(typeof L!=='undefined'){{init();}}
  else{{
    var s=document.createElement('script');
    s.src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    s.onload=init;
    document.head.appendChild(s);
  }}
}})();
</script>"""
        return mark_safe(html)

    map_preview.short_description = ''