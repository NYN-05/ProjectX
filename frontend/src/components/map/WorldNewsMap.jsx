import React, { useMemo } from 'react';
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';

const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

const COUNTRY_CENTER = {
  US: [-95.7129, 37.0902],
  GB: [-3.4360, 55.3781],
  IN: [78.9629, 20.5937],
  CN: [104.1954, 35.8617],
  JP: [138.2529, 36.2048],
  DE: [10.4515, 51.1657],
  FR: [2.2137, 46.2276],
  RU: [105.3188, 61.5240],
  AU: [133.7751, -25.2744],
  CA: [-106.3468, 56.1304],
  BR: [-51.9253, -14.2350],
  ES: [-3.7492, 40.4637],
  IT: [12.5674, 41.8719],
  KR: [127.7669, 35.9078],
  MX: [-102.5528, 23.6345],
  ID: [113.9213, -0.7893],
  TR: [35.2433, 38.9637],
  SA: [45.0792, 23.8859],
  ZA: [22.9375, -30.5595],
  NG: [8.6753, 9.0820],
};

export function WorldNewsMap({ mapData, onCountrySelect, selectedCountry, loading }) {
  const maxCount = useMemo(() => {
    if (!mapData?.countries) return 1;
    return Math.max(...mapData.countries.map(c => c.count), 1);
  }, [mapData]);

  const colorScale = useMemo(() => {
    return scaleLinear()
      .domain([0, maxCount])
      .range(['var(--accent-dim)', 'var(--accent)']);
  }, [maxCount]);

  const getCountryColor = (countryCode) => {
    if (!mapData?.countries) return 'var(--bg-elevated)';
    const country = mapData.countries.find(c => c.country_code === countryCode);
    if (!country) return 'var(--bg-elevated)';
    if (countryCode === selectedCountry) return 'var(--accent)';
    return colorScale(country.count);
  };

  const handleCountryClick = (geo) => {
    const countryCode = geo.properties.ISO_A3;
    onCountrySelect(countryCode);
  };

  const handleMarkerClick = (code) => {
    onCountrySelect(code);
  };

  return (
    <div className="world-map-container" style={{ width: '100%', height: '100%', minHeight: 400 }}>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ background: 'var(--bg-surface)', zIndex: 10 }}>
          <div className="text-center">
            <div className="animate-spin" style={{ width: 40, height: 40, border: '2px solid var(--border)', borderTopColor: 'var(--accent)', borderRadius: '50%', margin: '0 auto 12px' }} />
            <p style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'DM Mono, monospace' }}>Loading map data...</p>
          </div>
        </div>
      )}
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          scale: 120,
          center: [0, 20]
        }}
        style={{ width: '100%', height: '100%' }}
      >
        <ZoomableGroup>
          <Geographies geography={GEO_URL}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const isActive = mapData?.countries?.some(c => c.country_code === geo.properties.ISO_A3);
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    onClick={() => handleCountryClick(geo)}
                    style={{
                      default: {
                        fill: isActive ? getCountryColor(geo.properties.ISO_A3) : 'var(--bg-elevated)',
                        stroke: 'var(--border)',
                        strokeWidth: 0.5,
                        outline: 'none',
                      },
                      hover: {
                        fill: 'var(--accent)',
                        stroke: 'var(--accent)',
                        strokeWidth: 1,
                        outline: 'none',
                        cursor: 'pointer',
                      },
                      pressed: {
                        fill: 'var(--accent-hover)',
                        outline: 'none',
                      },
                    }}
                  />
                );
              })
            }
          </Geographies>
          
          {mapData?.heatmap?.map((point, i) => {
            const center = COUNTRY_CENTER[point.code] || [point.lng, point.lat];
            if (!center) return null;
            
            const size = Math.max(8, Math.min(30, (point.count / maxCount) * 30));
            
            return (
              <Marker
                key={i}
                coordinates={center}
                onClick={() => handleMarkerClick(point.code)}
                style={{
                  cursor: 'pointer',
                  outline: 'none'
                }}
              >
                <circle
                  r={size / 2}
                  fill={point.code === selectedCountry ? 'var(--accent)' : 'var(--accent)'}
                  fillOpacity={0.7}
                  stroke="var(--bg-base)"
                  strokeWidth={1}
                />
                <circle
                  r={size / 3}
                  fill="var(--accent)"
                  fillOpacity={0.9}
                />
              </Marker>
            );
          })}
        </ZoomableGroup>
      </ComposableMap>
    </div>
  );
}

export default WorldNewsMap;