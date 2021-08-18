const socket = new WebSocket(
    'wss://'
    + window.location.host
    + '/ws/upload-files/'
);

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data.message + '\n');
};

socket.onclose = function(event) {
  console.log('Socket closed!');
};

console.log(socket);

document.ready = function(){
    document.getElementById('btn-spinner').classList.add('not-visible');
    document.getElementById('btn-load').classList.remove('not-visible');
};

document.querySelector('#btn-load').onclick = function(){
    document.getElementById('btn-spinner').classList.remove('not-visible');
    document.getElementById('btn-load').classList.add('not-visible');

    var address_div = document.getElementById('address-file-location');
    var address_input = address_div.firstElementChild;

    address_input.onchange = function () { getFilename(address_input) };
    socket.send(JSON.stringify({
        'address_location': getFilename(address_input)
    }));
};

function getFilename(element){
    var filepath = element.value;
    var parts = filepath.split('\\');
    var filename = parts[parts.length - 1];
    return filename;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



