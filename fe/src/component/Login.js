import React from 'react';
import { Link } from 'react-router-dom';
import '../css/login.css'


export default class Login extends React.Component {
    render() {
        return (
            <div className="login-page">
                <div className="form">
                    <form className="login-form">
                        <input type="text" placeholder="邮箱"/>
                        <input type="password" placeholder="密码"/>
                        <button>登陆</button>
                        <p className="message">还未注册? <Link to="/reg">请注册</Link></p>
                    </form>
                </div>
            </div>
        )
    }
}