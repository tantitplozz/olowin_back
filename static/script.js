document.getElementById('submitBtn').addEventListener('click', async () => {
    const taskInput = document.getElementById('taskInput');
    const outputArea = document.getElementById('output');
    const userTask = taskInput.value;

    if (!userTask) {
        alert('Please enter a task.');
        return;
    }

    // Clear previous output and show loading indicator (optional)
    outputArea.textContent = 'Running task...';

    try {
        const response = await fetch('/submit_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task: userTask }),
        });

        const result = await response.json();

        if (response.ok) {
            // Display the result (or status if result is not detailed)
            outputArea.textContent = JSON.stringify(result, null, 2); // Pretty print JSON
        } else {
            // Display error message from backend
            outputArea.textContent = `Error: ${result.error || response.statusText}`;
            outputArea.style.color = 'red'; // Highlight errors
        }
    } catch (error) {
        // Handle network errors or other exceptions
        outputArea.textContent = `An unexpected error occurred: ${error}`;
        outputArea.style.color = 'red'; // Highlight errors
        console.error('Fetch error:', error);
    }
}); 