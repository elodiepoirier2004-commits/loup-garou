const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, 'public')));

let players = [];
let gameState = 'LOBBY'; // LOBBY, NIGHT_WITCH, NIGHT_SEER, NIGHT_WEREWOLVES, DAY

io.on('connection', (socket) => {
    console.log('Nouveau joueur connecté : ' + socket.id);

    socket.on('joinGame', (name) => {
        if (players.length < 12) {
            players.push({ id: socket.id, name, role: null, alive: true });
            io.emit('updatePlayerList', players);
        }
    });

    socket.on('startGame', () => {
        const roles = ['Voyante', 'Sorcière', 'Loup-Garou', 'Loup-Garou', 'Villageois', 'Villageois'];
        // Mélange aléatoire (Fisher-Yates)
        let shuffledRoles = roles.sort(() => Math.random() - 0.5);
        
        players.forEach((p, i) => {
            p.role = shuffledRoles[i] || 'Villageois';
            io.to(p.id).emit('assignRole', p.role);
        });

        gameState = 'NIGHT_SEER';
        io.emit('gameStateUpdate', { state: gameState, players });
    });

    socket.on('disconnect', () => {
        players = players.filter(p => p.id !== socket.id);
        io.emit('updatePlayerList', players);
    });
});

server.listen(3000, () => console.log('Serveur lancé sur http://localhost:3000'));