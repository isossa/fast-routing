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
    var counter = 0;
    var date = new Date();

    const LIMIT = 400;
    while (counter < LIMIT) {
        socket.send(JSON.stringify({
            'counter': date.getTime()
        }));
        console.log('Counter ' + date.getTime() + '\n');
        counter++;
    }
    console.log('Keeping connection open.');
}

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received ' + data.message + '\n');
};

if (socket.readyState == WebSocket.OPEN) {
    socket.onopen();
};

console.log(ws_scheme);
console.log(socket);