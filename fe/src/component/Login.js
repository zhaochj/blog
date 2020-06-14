import React from 'react';
import { Link } from 'react-router-dom';
import { Redirect } from 'react-router';
import '../css/login.css'
import UserService from "../service/user";
import { observer } from 'mobx-react';


const service = new UserService();

export default class Login extends React.Component {
    render() {
        return <_Login service={service} />;  {/*采用这种方式注入props*/}
    }
}

@observer  // _Login组件成为观察者
class _Login extends React.Component {
    handleClick(event) {
        event.preventDefault();  // form方式提交数据时，需要阻止默认的刷新操作
        const fm = event.target.form;
        let email = fm[0].value;
        let pwd = fm[1].value;
        // 获取到用户名及密码后，需要异步调用后端的登陆接口。这里还是要想办法使用props的方式调用
        this.props["service"].login(email, pwd)  // this.props.service这种写法，IDE会有提示无法解析此变量

    }

    render() {
        // 登陆成功后跳转
        if (this.props["service"].succeed) {
            return <Redirect to="/" />
        }

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