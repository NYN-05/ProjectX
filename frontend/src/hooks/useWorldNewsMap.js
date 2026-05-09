import { useState, useEffect, useCallback } from 'react';
import { newsAPI } from '../services/api';

export function useWorldNewsMap() {
  const [mapData, setMapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState(null);

  const fetchMapData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await newsAPI.getMapData(200, categoryFilter);
      setMapData(response.data.data || response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, [categoryFilter]);

  useEffect(() => {
    fetchMapData();
  }, [fetchMapData]);

  const selectCountry = useCallback((countryCode) => {
    if (!mapData) return null;
    return mapData.countries.find(c => c.country_code === countryCode);
  }, [mapData]);

  const getHeatmapData = useCallback(() => {
    if (!mapData) return [];
    return mapData.heatmap || [];
  }, [mapData]);

  const getCountryByCode = useCallback((code) => {
    if (!mapData) return null;
    return mapData.countries.find(c => c.country_code === code);
  }, [mapData]);

  return {
    mapData,
    loading,
    error,
    selectedCountry,
    setSelectedCountry,
    categoryFilter,
    setCategoryFilter,
    fetchMapData,
    selectCountry,
    getHeatmapData,
    getCountryByCode
  };
}

export default useWorldNewsMap;