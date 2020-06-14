import React from 'react';
import axios from 'axios';
import store from 'store';
import { observable } from 'mobx'

//过期插件
import expirePlugin from "store/plugins/expire";
store.addPlugin(expirePlugin);


class UserService {
    @observable succeed = false;  // 可观察对象
    @observable errMsg = "";

    login(email, pwd) {
        //异步调用后端login接口
        axios.post('/api/user/login', {
            email: email,
            password: pwd
        })
            .then(response => {
                // console.log(response.data);
                // console.log(response.status);
                // console.log(response.statusText);
                // console.log(response.headers);
                // console.log(response.config);
                // 异常调用成功后，后端返回user对象和token，token需要持久化到localstorage
                store.set('token', response.data.token, new Date().getTime() + (8 * 3600 * 1000),);  // 过期时间8小时
                this.succeed = true;  // 改变观察对象数据，注意：如果要用this，则需要把function改写成箭头函数
            })
            .catch(error => {
                // console.log('~~~~~~~~~~~~', error);
                this.errMsg = '登陆失败，请检查用户名和密码';
            });
    }

    reg(name, email, pwd) {
        axios.post('/api/user/reg', {
            name: name,
            email: email,
            password: pwd
        })
            .then(response => {
                store.set('token', response.data.token, new Date().getTime() + (8 * 3600 * 1000),);
                this.succeed = true;
            })
            .catch(error => {
                // console.log('==========', error);
                this.errMsg = "注册失败，请稍后重试"
            });
    }

}

const userService = new UserService();
export default userService