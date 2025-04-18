#

import contextily as ctx

# Define map providers
PROVIDERS = {
    "OpenTopoMap": ctx.providers.OpenTopoMap,
    "OpenStreetMap": ctx.providers.OpenStreetMap.Mapnik,
    "StamenTerrain": ctx.providers.Stadia.StamenTerrain,
    "EsriNatGeoWorldMap": ctx.providers.Esri.NatGeoWorldMap,
    "EsriWorldPhysical": ctx.providers.Esri.WorldPhysical,
    "EsriShadedRelief": ctx.providers.Esri.WorldShadedRelief,
    "EsriWorldImagery": ctx.providers.Esri.WorldImagery,
    "EsriWorldStreetMap": ctx.providers.Esri.WorldStreetMap,
    "EsriWorldTerrain": ctx.providers.Esri.WorldTerrain,
    "EsriWorldTopoMap": ctx.providers.Esri.WorldTopoMap,
    "USGSImagery": ctx.providers.USGS.USImagery,
    "USImageryTopo": ctx.providers.USGS.USImageryTopo,
    "USTopo": ctx.providers.USGS.USTopo,
}