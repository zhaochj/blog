import React from 'react';
import { Link } from 'react-router-dom';
import '../css/login.css'


export default class Reg extends React.Component {
    render() {
        return (
            <div className="login-page">
                <div className="form">
                    <form className="register-form">
                        <input type="text" placeholder="姓名"/>
                        <input type="text" placeholder="邮箱"/>
                        <input type="password" placeholder="密码"/>
                        <input type="password" placeholder="确认密码"/>
                        <button>注册</button>
                        <p className="message">如果已注册?<Link to="/login">登陆</Link></p>
                    </form>
                </div>
            </div>
        )
    }
}