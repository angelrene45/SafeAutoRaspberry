// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require('firebase-functions');

// The Firebase Admin SDK to access the Firebase Realtime Database.
const admin = require('firebase-admin');
admin.initializeApp();

//topics
const topicWeight = "weight_sensor";
const topicImpact = "impact_sensor";
const topicCamera = "camera";

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////Notificaciones//////////////////////////////////////////////////////////////////////
/////////////////////////////////////Sensor weight////////////////////////////////////////////////////////////////////////
exports.pushNotificationWeightSensor = functions.database.ref('/devices/{mac}/sensors/weight').onWrite( (event,context) => {

    //obtiene el valor de la mac en el path {mac}
    const macDevice = context.params.mac;
    console.log("mac device => ",macDevice);

    //obtiene el valor actual del sensor de peso
    const weightValue = event.after.val();

    //esto indica que hay actividad en el sensor de peso y lo notificamos al usuario
    if(weightValue === 0){
        return event.after.ref.parent.child('status').once('value').then(snapshot => {
            //se obtiene el status de la alarma
            const status = snapshot.val();
            console.log("Alarm status =>",status);
    
            if(status){ //alarma activada
                return admin.database().ref('devices/'+macDevice+'/uid').once('value')
                                .then(function(snapshot){
                    var uid = snapshot.val();
                    console.log("user id => ",uid);

                    //esto actualiza el status de la camara para poder tomar la foto 
                    var refPhoto = admin.database().ref('devices/'+macDevice+'/camera');
                    refPhoto.update({
                        "status" :  true
                    });
                    
                    return admin.database().ref('users/'+uid+'/registrationTokens').once('value')
                        .then(function(tokensSnapshot){
    
                            const tokens = tokensSnapshot.val();
                            console.log("Tokens => ",tokens);
    
                            const payload = {
                                notification: {
                                    title: 'Weight sensor',
                                    body: "Activity sensor!!!",
                                    sound: "default",
                                } ,
                                data: {
                                    alert: ".20" //hara que se pinte la notificacion en azul dentro de la aplicacion
                                }  
                            };
    
                            //return admin.messaging().sendToTopic(topicWeight,payload);
                            return admin.messaging().sendToDevice(tokens, payload);        
    
                        });
                });
            } //fin if status => true 
            else{ // status => false
                return null;
            }    
        });
    
    }else{ //valor de weigthValue => 1 no hay actividad en el sensor de peso
        return null;
    }
  
    
});

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////Notificaciones//////////////////////////////////////////////////////////////////////
/////////////////////////////////////Sensor weight////////////////////////////////////////////////////////////////////////
exports.pushNotificationImpactSensor = functions.database.ref('/devices/{mac}/sensors/impact').onWrite( (event,context) => {

    //obtiene el valor de la mac en el path {mac}
    const macDevice = context.params.mac;
    console.log("mac device => ",macDevice);

    //obtiene el valor actual del sensor de peso
    const impactValue = event.after.val();

    //esto indica que hay actividad en el sensor de impacto y lo notificamos al usuario
    if(impactValue === 1){
        return event.after.ref.parent.child('status').once('value').then(snapshot => {
            //se obtiene el status de la alarma
            const status = snapshot.val();
            console.log("Alarm status =>",status);
    
            if(status){ //alarma activada status => true
                return admin.database().ref('devices/'+macDevice+'/uid').once('value')
                                .then(function(snapshot){
                    var uid = snapshot.val();
                    console.log("user id => ",uid);

                    
                    return admin.database().ref('users/'+uid+'/registrationTokens').once('value')
                        .then(function(tokensSnapshot){
    
                            const tokens = tokensSnapshot.val();
                            console.log("Tokens => ",tokens);
    
                            const payload = {
                                notification: {
                                    title: 'Impact Sensor',
                                    body: "Activity sensor!!!",
                                    sound: "default",
                                } ,
                                data: {
                                    alert: ".50" //hara que se pinte la notificacion en azul dentro de la aplicacion
                                }  
                            };
    
                            //return admin.messaging().sendToTopic(topicWeight,payload);
                            return admin.messaging().sendToDevice(tokens, payload);        
    
                        });
                });
            }
            else{ // status => false
                return null;
            }    
        });
    
    }else{ //valor de weigthValue => 0 no hay actividad en el sensor de impacto
        return null;
    }
  
});