// Form submission functions
function submitForm() {
  console.log('submitForm called');
  document.getElementById('pageInput').value = '1'; // Reset to first page when filtering
  document.getElementById('filterForm').submit();
}

function sortBy(column) {
  console.log('sortBy called with column:', column);
  
  // Get current sort values from the hidden inputs
  const currentSort = document.getElementById('sortInput').value;
  const currentOrder = document.getElementById('orderInput').value;
  console.log('Current sort:', currentSort, 'Current order:', currentOrder);
  
  let newOrder = 'desc';
  if (currentSort === column) {
    newOrder = currentOrder === 'desc' ? 'asc' : 'desc';
  }
  
  console.log('Setting new sort:', column, 'New order:', newOrder);
  document.getElementById('sortInput').value = column;
  document.getElementById('orderInput').value = newOrder;
  document.getElementById('pageInput').value = '1'; // Reset to first page when sorting
  
  console.log('Submitting form...');
  document.getElementById('filterForm').submit();
}

// Jump to specific page functionality
function jumpToPage() {
  const pageInput = document.getElementById('jumpToPageInput');
  const pageNumber = parseInt(pageInput.value);
  const maxPages = parseInt(document.querySelector('[data-max-pages]').getAttribute('data-max-pages'));
  
  if (pageNumber && pageNumber >= 1 && pageNumber <= maxPages) {
    const url = new URL(window.location.href);
    url.searchParams.set('page', pageNumber);
    window.location.href = url.toString();
  } else {
    alert('Please enter a page number between 1 and ' + maxPages);
  }
}

// Handle Enter key in search and jump inputs
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const jumpInput = document.getElementById('jumpToPageInput');
  
  if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        submitForm();
      }
    });
  }
  
  if (jumpInput) {
    jumpInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        jumpToPage();
      }
    });
  }
  
  console.log('players.js loaded successfully');
});

// Season/Date selector functions (for future use)
function updateAvailableDates() {
  const season = document.getElementById('season-select').value;
  fetch(`/api/dates/${season}`)
    .then(response => response.json())
    .then(dates => {
      const dateSelect = document.getElementById('date-select');
      dateSelect.innerHTML = '<option value="current">Latest Data</option>';
      dates.forEach(date => {
        const option = document.createElement('option');
        option.value = date.date;
        option.textContent = date.display_name;
        if (date.is_current) option.selected = true;
        dateSelect.appendChild(option);
      });
    })
    .catch(error => console.error('Error loading dates:', error));
}

function updatePlayerData() {
  const season = document.getElementById('season-select').value;
  const date = document.getElementById('date-select').value;
  
  // Show loading indicator
  const tableContainer = document.querySelector('.table-responsive');
  tableContainer.innerHTML = '<div class="text-center p-4"><i class="fas fa-spinner fa-spin"></i> Loading player data...</div>';
  
  // Reload page with new parameters
  const url = new URL(window.location.href);
  url.searchParams.set('season', season);
  url.searchParams.set('date', date);
  window.location.href = url.toString();
}

function loadSeasonData() {
  fetch('/api/seasons')
    .then(response => response.json())
    .then(seasons => {
      const seasonSelect = document.getElementById('season-select');
      if (seasonSelect) {
        seasonSelect.innerHTML = '';
        seasons.forEach(season => {
          const option = document.createElement('option');
          option.value = season.season;
          option.textContent = season.display_name;
          if (season.is_active) option.selected = true;
          seasonSelect.appendChild(option);
        });
        
        // Load dates for current season
        updateAvailableDates();
      }
    })
    .catch(error => console.error('Error loading seasons:', error));
}
