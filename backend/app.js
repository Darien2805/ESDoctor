// mdc.ripple.MDCRipple.attachTo(document.querySelector('.mdc-button'));


const firebaseConfig = {

  apiKey: "AIzaSyC39QBbBwk0E5HDddnUV_ZFwPMBrhGQmno",

  authDomain: "esdproject-telemedicine.firebaseapp.com",

  projectId: "esdproject-telemedicine",

  storageBucket: "esdproject-telemedicine.appspot.com",

  messagingSenderId: "1045290834485",

  appId: "1:1045290834485:web:03be3baf4aba47ada16f7c"

}


firebase.initializeApp(firebaseConfig)
// DEfault configuration - Change these if you have a different STUN or TURN server.
const configuration = {
  iceServers: [
    {
      urls: [
        'stun:stun1.l.google.com:19302',
        'stun:stun2.l.google.com:19302',
      ],
    },
  ],
  iceCandidatePoolSize: 10,
};

let peerConnection = null;
let localStream = null;
let remoteStream = null;
let roomDialog = null;
let roomId = null;

function init() {
  document.querySelector('#cameraBtn').addEventListener('click', openUserMedia);
  document.querySelector('#hangupBtn').addEventListener('click', hangUp);
  roomDialog = new mdc.dialog.MDCDialog(document.querySelector('#room-dialog'));
  document.querySelector('#joinBtn').addEventListener('click', joinRoom);

}

async function createRoom() {
  document.querySelector('#createBtn').disabled = true;
  document.querySelector('#joinBtn').disabled = true;

  console.log('Create PeerConnection with configuration: ', configuration);
  peerConnection = new RTCPeerConnection(configuration);

  registerPeerConnectionListeners();

  localStream.getTracks().forEach(track => {
    peerConnection.addTrack(track, localStream);
  });
  // Code for collecting ICE candidates below
  const callerCandidatesCollection = roomRef.collection('callerCandidates');

  peerConnection.addEventListener('icecandidate', event => {
    if (!event.candidate) {
        console.log('Got final candidate!');
        return;
      }
      console.log('Got candidate: ', event.candidate);
      callerCandidatesCollection.add(event.candidate.toJSON());
  });
  // Add code for creating a room here

  const offer = await peerConnection.createOffer();
  await peerConnection.setLocalDescription(offer);
  console.log('Created offer:', offer);

  const roomWithOffer = {
      offer: {
          type: offer.type,
          sdp: offer.sdp
      }
  }
  
  await roomRef.set(roomWithOffer);
  const roomId = roomRef.id;
  document.querySelector('#currentRoom').innerText = `Current room is ${roomId} - You are the caller!`

  peerConnection.addEventListener('track', event => {
    console.log('Got remote track:', event.streams[0]);
    event.streams[0].getTracks().forEach(track => {
      console.log('Add a track to the remoteStream:', track);
      remoteStream.addTrack(track);
    });
  });
  // Listening for remote session description below

  roomRef.onSnapshot(async snapshot => {
      console.log('Got updated room:', snapshot.data());
      const data = snapshot.data();
      console.log(data.offer)
     
      if (!peerConnection.currentRemoteDescription && data.answer) {
          console.log('Set remote description: ', data.answer);
          const answer = new RTCSessionDescription(data.answer)
          await peerConnection.setRemoteDescription(answer);
      }
      
  });
  
  roomRef.collection('calleeCandidates').onSnapshot(snapshot => {
    snapshot.docChanges().forEach(async change => {
      if (change.type === 'added') {
        let data = change.doc.data();
        console.log(`Got new remote ICE candidate: ${JSON.stringify(data)}`);
        await peerConnection.addIceCandidate(new RTCIceCandidate(data));
      }
    });
  });

  // end code for Create Room
  
  // Code for creating room above
  
  // localStream.getTracks().forEach(track => {
  //   peerConnection.addTrack(track, localStream);
  // });

  // Code for creating a room below

  // Code for creating a room above

  // Code for collecting ICE candidates below
  async function collectIceCandidates(roomRef, peerConnection,
    localName, remoteName) {
    const candidatesCollection = roomRef.collection(localName);

    peerConnection.addEventListener('icecandidate', event => {
    if (event.candidate) {
    const json = event.candidate.toJSON();
    candidatesCollection.add(json);
    }
    });

    roomRef.collection(remoteName).onSnapshot(snapshot => {
    snapshot.docChanges().forEach(change => {
    if (change.type === "added") {
    const candidate = new RTCIceCandidate(change.doc.data());
    peerConnection.addIceCandidate(candidate);
    }
    });
    })
    }

  // Code for collecting ICE candidates above


  // Listening for remote session description below

  // Listening for remote session description above

  // Listen for remote ICE candidates below

  // Listen for remote ICE candidates above
}

function joinRoom() {

  document.querySelector('#joinBtn').disabled = true;

  document.querySelector('#confirmJoinBtn').
      addEventListener('click', async () => {
        roomId = document.querySelector('#room-id').value;
        console.log('Join room: ', roomId);
        await joinRoomById(roomId);
      }, {once: true});
  roomDialog.open();
}

async function joinRoomById(roomId) {
  const db = firebase.firestore();
  const roomRef = db.collection('rooms').doc(`${roomId}`);
  const roomSnapshot = await roomRef.get();
  console.log('Got room:', roomSnapshot.exists);
  
  if (roomSnapshot.exists) {
    console.log('Create PeerConnection with configuration: ', configuration);
    peerConnection = new RTCPeerConnection(configuration);
  
    registerPeerConnectionListeners();
  
    localStream.getTracks().forEach(track => {
      peerConnection.addTrack(track, localStream);
    });
    // Code for collecting ICE candidates below
    const callerCandidatesCollection = roomRef.collection('callerCandidates');
  
    peerConnection.addEventListener('icecandidate', event => {
      if (!event.candidate) {
          console.log('Got final candidate!');
          return;
        }
        console.log('Got candidate: ', event.candidate);
        callerCandidatesCollection.add(event.candidate.toJSON());
    });
    // Add code for creating a room here
  
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    console.log('Created offer:', offer);
  
    const roomWithOffer = {
        offer: {
            type: offer.type,
            sdp: offer.sdp
        }
    }
    
    await roomRef.set(roomWithOffer);
    

    peerConnection.addEventListener('track', event => {
      console.log('Got remote track:', event.streams[0]);
      event.streams[0].getTracks().forEach(track => {
        console.log('Add a track to the remoteStream:', track);
        remoteStream.addTrack(track);
      });
    });
    // Listening for remote session description below
  
    roomRef.onSnapshot(async snapshot => {
        console.log('Got updated room:', snapshot.data());
        const data = snapshot.data();
        console.log(data.offer)
       
        if (!peerConnection.currentRemoteDescription && data.answer) {
            console.log('Set remote description: ', data.answer);
            const answer = new RTCSessionDescription(data.answer)
            await peerConnection.setRemoteDescription(answer);
        }
        
    });
    
    roomRef.collection('calleeCandidates').onSnapshot(snapshot => {
      snapshot.docChanges().forEach(async change => {
        if (change.type === 'added') {
          let data = change.doc.data();
          console.log(`Got new remote ICE candidate: ${JSON.stringify(data)}`);
          await peerConnection.addIceCandidate(new RTCIceCandidate(data));
        }
      });
    });
  
    // end code for Create Room
    
    // Code for creating room above
    
    // localStream.getTracks().forEach(track => {
    //   peerConnection.addTrack(track, localStream);
    // });
  
    // Code for creating a room below
  
    // Code for creating a room above
  
    // Code for collecting ICE candidates below
    async function collectIceCandidates(roomRef, peerConnection,
      localName, remoteName) {
      const candidatesCollection = roomRef.collection(localName);
  
      peerConnection.addEventListener('icecandidate', event => {
      if (event.candidate) {
      const json = event.candidate.toJSON();
      candidatesCollection.add(json);
      }
      });
  
      roomRef.collection(remoteName).onSnapshot(snapshot => {
      snapshot.docChanges().forEach(change => {
      if (change.type === "added") {
      const candidate = new RTCIceCandidate(change.doc.data());
      peerConnection.addIceCandidate(candidate);
      }
      });
      })
      }

  }
  console.log('RemoteStream after get room2:', document.querySelector('#remoteVideo').srcObject);
}

async function openUserMedia(e) {
  const stream = await navigator.mediaDevices.getUserMedia(
      {video: true, audio: true});
  document.querySelector('#localVideo').srcObject = stream;
  localStream = stream;
  remoteStream = new MediaStream();
  document.querySelector('#remoteVideo').srcObject = remoteStream;

  console.log('Stream:', document.querySelector('#localVideo').srcObject);
  
  document.querySelector('#cameraBtn').disabled = true;
  document.querySelector('#joinBtn').disabled = false;

  document.querySelector('#hangupBtn').disabled = false;
}

async function hangUp(e) {
  const tracks = document.querySelector('#localVideo').srcObject.getTracks();
  tracks.forEach(track => {
    track.stop();
  });

  if (remoteStream) {
    remoteStream.getTracks().forEach(track => track.stop());
    console.log('RemoteStream:', document.querySelector('#remoteVideo').srcObject);
  }

  if (peerConnection) {
    peerConnection.close();
  }

  document.querySelector('#localVideo').srcObject = null;
  document.querySelector('#remoteVideo').srcObject = null;
  document.querySelector('#cameraBtn').disabled = false;
  document.querySelector('#joinBtn').disabled = true;
  document.querySelector('#hangupBtn').disabled = true;
  //document.querySelector('#currentRoom').innerText = '';

  // Delete room on hangup
  if (roomId) {
    /*
    const db = firebase.firestore();
    const roomRef = db.collection('rooms').doc(roomId);
    const calleeCandidates = await roomRef.collection('calleeCandidates').get();
    calleeCandidates.forEach(async candidate => {
      await candidate.delete();
    });
    const callerCandidates = await roomRef.collection('callerCandidates').get();
    callerCandidates.forEach(async candidate => {
      await candidate.delete();
    });
    await roomRef.delete();
    console.log("room successfully deleted")
  }
  */  
      console.log('in')
      window.location.replace("./doctor_prescribe.html"+"?roomID="+roomId)
    }
  // document.location.reload(true);
}

function registerPeerConnectionListeners() {
  peerConnection.addEventListener('icegatheringstatechange', () => {
    console.log(
        `ICE gathering state changed: ${peerConnection.iceGatheringState}`);
  });

  peerConnection.addEventListener('connectionstatechange', () => {
    console.log(`Connection state change: ${peerConnection.connectionState}`);
  });

  peerConnection.addEventListener('signalingstatechange', () => {
    console.log(`Signaling state change: ${peerConnection.signalingState}`);
  });

  peerConnection.addEventListener('iceconnectionstatechange ', () => {
    console.log(
        `ICE connection state change: ${peerConnection.iceConnectionState}`);
  });


}

init();
