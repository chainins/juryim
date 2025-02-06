document.addEventListener('DOMContentLoaded', function() {
    // Handle withdrawal approval
    document.querySelectorAll('.approve-withdrawal').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            confirmAction('Are you sure you want to approve this withdrawal?', form);
        });
    });

    // Handle withdrawal rejection
    document.querySelectorAll('.reject-withdrawal').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            const reason = prompt('Please enter rejection reason:');
            if (reason) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'reason';
                input.value = reason;
                form.appendChild(input);
                form.submit();
            }
        });
    });

    // Real-time status updates
    const withdrawalIds = Array.from(document.querySelectorAll('[data-withdrawal-id]'))
        .map(el => el.dataset.withdrawalId);
    
    if (withdrawalIds.length > 0) {
        setInterval(() => {
            fetch(`/api/withdrawals/status/?ids=${withdrawalIds.join(',')}`)
                .then(response => response.json())
                .then(data => {
                    Object.entries(data).forEach(([id, status]) => {
                        const statusEl = document.querySelector(`[data-withdrawal-id="${id}"] .status`);
                        if (statusEl) {
                            statusEl.textContent = status;
                            statusEl.className = `status status-${status.toLowerCase()}`;
                        }
                    });
                });
        }, 30000); // Update every 30 seconds
    }
}); 