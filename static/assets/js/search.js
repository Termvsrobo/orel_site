(function() {
    const searchButton = document.querySelector('#search')
    const clearButton = document.querySelector('#clearInput')
    const searchInput = document.querySelector('#searchInput')

    searchButton.addEventListener('click', event => {
        const searchText = searchInput.value
        if (searchText) {
            window.location.href = `/search?search=${searchText}`
        }
    })
    
    clearButton.addEventListener('click', event => {
        searchInput.value = ''
    })
})()