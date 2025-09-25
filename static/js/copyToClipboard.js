/**
 * Enhanced clipboard copy functionality with fallback support
 */

function copyToClipboard(text) {
    // Try modern clipboard API first
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(event.target);
        }).catch(function(err) {
            console.error('Clipboard API failed: ', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        // Fallback for older browsers or non-secure contexts
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    // Create a temporary textarea element
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(event.target);
        } else {
            showCopyError(event.target);
        }
    } catch (err) {
        console.error('Fallback copy failed: ', err);
        showCopyError(event.target);
    }
    
    document.body.removeChild(textArea);
}

function showCopySuccess(button) {
    const originalText = button.textContent || button.innerHTML;
    const isHTML = button.innerHTML !== button.textContent;
    
    if (isHTML) {
        button.innerHTML = '<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Copied!';
    } else {
        button.textContent = '✅ Copied!';
    }
    
    button.classList.add('bg-green-600', 'hover:bg-green-700');
    button.classList.remove('bg-white', 'hover:bg-gray-50', 'bg-primary-500', 'hover:bg-primary-600');
    
    setTimeout(() => {
        if (isHTML) {
            button.innerHTML = originalText;
        } else {
            button.textContent = originalText;
        }
        button.classList.remove('bg-green-600', 'hover:bg-green-700');
        button.classList.add('bg-white', 'hover:bg-gray-50');
    }, 2000);
}

function showCopyError(button) {
    const originalText = button.textContent || button.innerHTML;
    const isHTML = button.innerHTML !== button.textContent;
    
    if (isHTML) {
        button.innerHTML = '<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>Failed!';
    } else {
        button.textContent = '❌ Failed';
    }
    
    button.classList.add('bg-red-600', 'hover:bg-red-700');
    button.classList.remove('bg-white', 'hover:bg-gray-50', 'bg-primary-500', 'hover:bg-primary-600');
    
    setTimeout(() => {
        if (isHTML) {
            button.innerHTML = originalText;
        } else {
            button.textContent = originalText;
        }
        button.classList.remove('bg-red-600', 'hover:bg-red-700');
        button.classList.add('bg-white', 'hover:bg-gray-50');
    }, 2000);
}
