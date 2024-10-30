document.addEventListener('DOMContentLoaded', function() {
    const loadMoreButton = document.getElementById('load-more');
    const projectsContainer = document.getElementById('projects-container');
    const currentYearSpan = document.getElementById('current-year');

    // Set current year in footer
    currentYearSpan.textContent = new Date().getFullYear();

    loadMoreButton.addEventListener('click', function() {
        fetch('/load_more_projects')
            .then(response => response.json())
            .then(data => {
                data.forEach(project => {
                    const projectElement = createProjectElement(project);
                    projectsContainer.appendChild(projectElement);
                });
                loadMoreButton.style.display = 'none';
            })
            .catch(error => console.error('Error:', error));
    });

    function createProjectElement(project) {
        const div = document.createElement('div');
        div.className = 'card';
        div.innerHTML = `
            <div class="p-6 space-y-4">
                <h3 class="text-2xl font-bold">${project.name}</h3>
                <p class="text-muted-foreground">${project.description}</p>
                <img src="${project.image}" alt="Preview of ${project.name}" class="rounded-lg shadow-lg w-full object-cover">
                <a href="${project.link}" class="btn btn-primary w-full">
                    View Project
                    <svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </a>
            </div>
        `;
        return div;
    }
});