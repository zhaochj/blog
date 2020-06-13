import React from 'react';
import axios from 'axios';


export default class UserService {
    login(email, pwd) {
        //异步调用后端login接口
        axios.post('/api/user/login', {
            email: email,
            password: pwd
        })
            .then(function (response) {
                console.log(response.data);
                console.log(response.status);
                console.log(response.statusText);
                console.log(response.headers);
                console.log(response.config);
            })
            .catch(function (error) {
                console.log('~~~~~~~~~~~~', error);
            });
    }

}