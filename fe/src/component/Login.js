import React from 'react';
import { Link } from 'react-router-dom';
import '../css/login.css'
import UserService from "../service/user";

const service = new UserService();

export default class Login extends React.Component {
    render() {
        return <_Login service={service} />;  {/*采用这种方式注入props*/}
    }
}


class _Login extends React.Component {
    handleClick(event) {
        event.preventDefault();  // form方式提交数据时，需要阻止默认的刷新操作
        const fm = event.target.form;
        let email = fm[0].value;
        let pwd = fm[1].value;
        // 获取到用户名及密码后，需要异步调用后端的登陆接口。这里还是要想办法使用props的方式调用
        this.props.service.login(email, pwd)

    }

    render() {
        return (
            <div className="login-page">
                <div className="form">
                    <form className="login-form">
                        <input type="text" placeholder="邮箱"/>
                        <input type="password" placeholder="密码"/>
                        <button onClick={this.handleClick.bind(this)}>登陆</button>
                        <p className="message">还未注册? <Link to="/reg">请注册</Link></p>
                    </form>
                </div>
            </div>
        )
    }
}