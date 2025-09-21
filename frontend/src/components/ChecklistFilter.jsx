import { useState } from 'react'

const ChecklistFilter = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    category: '',
    status: '',
    criticality: ''
  })

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  const clearFilters = () => {
    const clearedFilters = {
      category: '',
      status: '',
      criticality: ''
    }
    setFilters(clearedFilters)
    onFilterChange(clearedFilters)
  }

  return (
    <div className="checklist-filters">
      <h3>Filter Checklist</h3>
      
      <div className="filters-grid">
        <div className="filter-group">
          <label htmlFor="category-filter">Category:</label>
          <select
            id="category-filter"
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="safety">Safety</option>
            <option value="security">Security</option>
            <option value="backup">Backup</option>
            <option value="network">Network</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="status-filter">Status:</label>
          <select
            id="status-filter"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="">All Status</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="criticality-filter">Criticality:</label>
          <select
            id="criticality-filter"
            value={filters.criticality}
            onChange={(e) => handleFilterChange('criticality', e.target.value)}
          >
            <option value="">All Tasks</option>
            <option value="critical">Critical Only</option>
            <option value="non-critical">Non-Critical Only</option>
          </select>
        </div>

        <div className="filter-group">
          <button onClick={clearFilters} className="button button-secondary">
            Clear Filters
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChecklistFilter