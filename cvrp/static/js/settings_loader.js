var ws_scheme = window.location.protocol == 'https:' ? 'wss' : 'ws';

const socket = new WebSocket(
    ws_scheme
    + '://'
    + window.location.host
    + '/ws/settings/load/'
);

socket.onclose = function(event) {
    console.log('Socket closed!');
};

socket.onopen = function(event) {
    console.log('Keeping connection open');
    socket.send(JSON.stringify({
            'update_matrix': document.getElementById('id_update_distance_matrix').textContent.trim(),
            'message': 'Ready'
    }));
}

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received ' + data.message + '\n');
    if (data.message == 'DONE') {
        console.log('Finished uploading!');
        var http_scheme = window.location.protocol
        url = http_scheme + '//' + window.location.host + '/cvrp/routes/create_routes/';
        window.location.replace(url);
        console.log(url);
    }
};

socket.onerror = function(event) {
    console.log('An error occurred with message: ' + event.data);
}

console.log(ws_scheme);
console.log(socket);
console.log(document.getElementById('id_update_distance_matrix').textContent);