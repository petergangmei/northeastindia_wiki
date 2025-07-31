document.addEventListener('DOMContentLoaded', function() {
    // Initialize info box widget functionality
    initInfoBoxWidget();
});

function initInfoBoxWidget() {
    // Handle adding new label-value pairs
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('add-pair')) {
            addInfoBoxPair(e.target);
        }
    });
    
    // Handle removing label-value pairs
    document.addEventListener('click', function(e) {
        if (e.target && (e.target.classList.contains('remove-pair') || e.target.closest('.remove-pair'))) {
            removeInfoBoxPair(e.target.closest('.remove-pair'));
        }
    });
    
    // Ensure at least one pair is always present
    document.querySelectorAll('.info-box-data-widget').forEach(function(widget) {
        const pairs = widget.querySelectorAll('.info-box-pair');
        if (pairs.length === 0) {
            const addButton = widget.querySelector('.add-pair');
            if (addButton) {
                addInfoBoxPair(addButton);
            }
        }
    });
}

function addInfoBoxPair(addButton) {
    const targetId = addButton.getAttribute('data-target');
    const fieldName = addButton.getAttribute('data-name');
    const container = document.getElementById(targetId);
    
    if (!container) return;
    
    // Create new pair element
    const newPair = document.createElement('div');
    newPair.className = 'info-box-pair row mb-2';
    newPair.innerHTML = `
        <div class="col-md-4">
            <input type="text" 
                   name="${fieldName}_label" 
                   value="" 
                   placeholder="Label (e.g., Name)" 
                   class="form-control info-box-label">
        </div>
        <div class="col-md-6">
            <input type="text" 
                   name="${fieldName}_value" 
                   value="" 
                   placeholder="Value (e.g., Peter)" 
                   class="form-control info-box-value">
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-outline-danger btn-sm remove-pair">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    // Add the new pair to the container
    container.appendChild(newPair);
    
    // Focus on the label input of the new pair
    const labelInput = newPair.querySelector('.info-box-label');
    if (labelInput) {
        labelInput.focus();
    }
    
    // Update count
    updatePairCount(container);
}

function removeInfoBoxPair(removeButton) {
    const pair = removeButton.closest('.info-box-pair');
    const container = pair.closest('.info-box-pairs');
    
    if (!pair || !container) return;
    
    // Don't remove if it's the only pair
    const pairs = container.querySelectorAll('.info-box-pair');
    if (pairs.length <= 1) {
        // Clear the inputs instead of removing
        const labelInput = pair.querySelector('.info-box-label');
        const valueInput = pair.querySelector('.info-box-value');
        if (labelInput) labelInput.value = '';
        if (valueInput) valueInput.value = '';
        return;
    }
    
    // Remove the pair
    pair.remove();
    
    // Update count
    updatePairCount(container);
}

function updatePairCount(container) {
    const widget = container.closest('.info-box-data-widget');
    const countInput = widget.querySelector('[name$="_count"]');
    if (countInput) {
        const pairs = container.querySelectorAll('.info-box-pair');
        countInput.value = pairs.length;
    }
}

// Add some helpful features
document.addEventListener('input', function(e) {
    if (e.target && e.target.classList.contains('info-box-label')) {
        // Auto-suggest common labels based on content type
        const commonLabels = {
            'person': ['Name', 'Born', 'Died', 'Occupation', 'Known for', 'Years active', 'Nationality'],
            'place': ['Location', 'Coordinates', 'Type', 'Watercourse', 'Known as', 'District', 'State'],
            'movie': ['Director', 'Producer', 'Writer', 'Starring', 'Music by', 'Release date', 'Running time', 'Budget', 'Box office', 'Language', 'Country']
        };
        
        // This could be enhanced with a dropdown suggestion feature
        // For now, we'll just add a title attribute with suggestions
        const contentTypeField = document.querySelector('[name="content_type"]');
        if (contentTypeField) {
            const contentType = contentTypeField.value;
            const suggestions = commonLabels[contentType] || [];
            if (suggestions.length > 0) {
                e.target.setAttribute('title', 'Common labels: ' + suggestions.join(', '));
            }
        }
    }
});