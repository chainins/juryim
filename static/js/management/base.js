// Confirmation dialogs
function confirmAction(message, form) {
    if (confirm(message)) {
        form.submit();
    }
    return false;
}

// Table sorting and filtering
document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('.table-sortable');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.dataset.sort;
                sortTable(table, column);
            });
        });
    });
});

// Search functionality
document.getElementById('table-search')?.addEventListener('input', function(e) {
    const searchText = e.target.value.toLowerCase();
    const table = document.querySelector('.table-searchable');
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchText) ? '' : 'none';
    });
});

// AJAX form submission
function submitFormAjax(form, successCallback) {
    const formData = new FormData(form);
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            successCallback(data);
        } else {
            alert(data.error || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred');
    });
}

// CSRF token helper
function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
} 