// This file can be used for any client-side JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add any JavaScript that needs to run when the page loads
    console.log('BFL APPAREL website loaded');
    
    // Example: Toast notifications
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl).show();
    });
});
// Payment method toggle
function setupPaymentMethodToggle() {
    const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
    const mpesaFields = document.getElementById('mpesaFields');
    
    if (!paymentMethods.length || !mpesaFields) return;
    
    function toggleFields() {
        const selectedMethod = document.querySelector('input[name="payment_method"]:checked').value;
        mpesaFields.style.display = selectedMethod === 'mpesa' ? 'block' : 'none';
    }
    
    paymentMethods.forEach(method => {
        method.addEventListener('change', toggleFields);
    });
    
    // Initialize on load
    toggleFields();
}

document.addEventListener('DOMContentLoaded', function() {
    setupPaymentMethodToggle();
});