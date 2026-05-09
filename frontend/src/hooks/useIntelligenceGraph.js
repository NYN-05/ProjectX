import { useState, useEffect, useCallback } from 'react';
import { newsAPI } from '../services/api';

export function useIntelligenceGraph() {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filters, setFilters] = useState({
    eventType: null,
    sector: null,
    country: null,
    impact: null
  });
  const [centralEvents, setCentralEvents] = useState([]);

  const buildGraph = useCallback(async () => {
    setLoading(true);
    try {
      const response = await newsAPI.buildGraph(100);
      const data = response.data.data || response.data;
      setGraphData(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchGraph = useCallback(async (filterParams = {}) => {
    setLoading(true);
    try {
      const params = { limit: 100, ...filterParams };
      const response = await newsAPI.getGraph(params);
      const data = response.data.data || response.data;
      setGraphData(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCentralEvents = useCallback(async () => {
    try {
      const response = await newsAPI.getCentralEvents(10);
      setCentralEvents(response.data.data?.events || []);
    } catch (err) {
      console.error('Failed to fetch central events:', err);
    }
  }, []);

  useEffect(() => {
    buildGraph();
    fetchCentralEvents();
  }, [buildGraph, fetchCentralEvents]);

  useEffect(() => {
    if (filters.eventType || filters.sector || filters.country || filters.impact) {
      fetchGraph({
        event_type: filters.eventType,
        sector: filters.sector,
        country: filters.country,
        impact: filters.impact
      });
    }
  }, [filters, fetchGraph]);

  const selectEvent = useCallback(async (eventId) => {
    try {
      const response = await newsAPI.getEventDetail(eventId);
      setSelectedEvent(response.data.data);
    } catch (err) {
      console.error('Failed to fetch event detail:', err);
    }
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      eventType: null,
      sector: null,
      country: null,
      impact: null
    });
    buildGraph();
  }, [buildGraph]);

  return {
    graphData,
    loading,
    error,
    selectedEvent,
    setSelectedEvent,
    filters,
    setFilters,
    clearFilters,
    buildGraph,
    fetchGraph,
    selectEvent,
    centralEvents
  };
}

export default useIntelligenceGraph;