const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, 'public')));

let players = [];
let currentIndex = 0;
const phases = ['NIGHT_WEREWOLVES', 'NIGHT_SEER', 'NIGHT_WITCH', 'DAY_VOTE'];

io.on('connection', (socket) => {
    socket.on('joinGame', (name) => {
        if (!players.find(p => p.id === socket.id)) {
            players.push({ id: socket.id, name, role: null, alive: true });
        }
        io.emit('updatePlayerList', players);
    });

    socket.on('startGame', () => {
        if (players.length < 1) return; // Pour tester seul, sinon mets 4

        // Distribution simplifiée
        const rolesPool = ['Loup-Garou', 'Voyante', 'Sorcière', 'Villageois', 'Villageois', 'Villageois'];
        players.forEach((p, i) => {
            p.role = rolesPool[i] || 'Villageois';
            p.alive = true;
            io.to(p.id).emit('assignRole', p.role);
        });

        sendPhaseUpdate('NIGHT_WEREWOLVES');
    });

    function sendPhaseUpdate(phase) {
        io.emit('gameStateUpdate', { 
            phase: phase, 
            players: players.map(p => ({ name: p.name, alive: p.alive, id: p.id })) 
        });
    }

    // Ici on pourrait ajouter les socket.on('vote') etc.
});

server.listen(3000, () => console.log('Prêt sur http://localhost:3000'));
