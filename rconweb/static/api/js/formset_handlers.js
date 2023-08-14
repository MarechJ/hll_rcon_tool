document.addEventListener('formset:added', (event) => {
    const formsetName = event.detail.formsetName
    if (formsetName === 'djangoapikey_set') {
        const apiKey = document.getElementById(`id_${event.target.id}-api_key`)
        apiKey.value = window.uuidv4()
    }    
});

document.addEventListener('readystatechange', event => { 

    if (event.target.readyState === "complete") {
        const elementSearch = `id_api_key`
        const apiKey = document.getElementById(elementSearch)
        apiKey.value = window.uuidv4()
    }
});