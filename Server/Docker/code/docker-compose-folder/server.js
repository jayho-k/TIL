// const express = require("express");
// const redis = require("redis");

// // create redic client 
// const client = redis.createClient({
//     //도커를 사용할땐 파일에 명시한 컨테이너 이름으로 주면된다.
//     //도커를 사용하지 않을땐 https://redis-server.com
//     socket:{
//         host:"redis-server", 
//         port:6379
//     }    
// })

// const app = express();

// // num=0
// app.get('/',async (req,res)=>{
//     await client.connect();
//     let number = await client.get('number');
//     if (number === null){
//         number = 0;
//     }
//     console.log('NUmber:'+number);
//     res.send("숫자가 1씩 올라갑니다. 숫자:"+number);
//     await client.set("number",parseInt(number)+1);
//     await client.disconnect();
// })

// app.listen(8080);
// console.log('server is running');


// const express = require("express");

// const redis = require("redis");



//레디스 클라이언트 생성 

const client = redis.createClient({
    socket: {
        host: "redis-server",
        port: 6379
    }
});

const app = express();

app.get('/', async (req, res) => {

    await client.connect();
    let number = await client.get('number');
    if (number === null) {
    number = 0;
    }

    console.log('Number: ' + number);
    res.send("숫자가 1씩 올라갑니다. 숫자: " + number)
    await client.set("number", parseInt(number) + 1)
    await client.disconnect();;;
})


app.listen(8080);
console.log('Server is running');