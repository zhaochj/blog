import React from 'react';
import { Link } from 'react-router-dom';
import { Redirect } from 'react-router'
import '../css/login.css'
import userService from "../service/user";
import { observer } from 'mobx-react';
import {message} from "antd";


export default class Reg extends React.Component {
    render() {
        return <_Reg service={userService}/>;
        //为了分出service这个层次，在组件层中需要想办法把service中的处理逻辑函数通过props的方式注入到组件中，所以采用这种在组件中再套一层的方式
    }
}

@observer
class _Reg extends React.Component {
    handleClick(event) {
        event.preventDefault();

        // form提交数据时，js提取数据方法
        let fm = event.target.form;
        let name = fm[0].value;
        let email = fm[1].value;
        let pwd = fm[2].value;
        this.props.service.reg(name, email, pwd);
    }

    render() {
        // 注册成功跳转
        if(this.props.service.succeed) {
            return <Redirect to="/"/>;
        }

        // 有错误信息时，页面友好提示
        if (this.props.service.errMsg) {
            message.error(this.props.service.errMsg, 3, () => {this.props.service.errMsg=""});
        }

        return (
            <div className="login-page">
                <div className="form">
                    <form className="register-form">
                        <input type="text" placeholder="姓名"/>
                        <input type="text" placeholder="邮箱"/>
                        <input type="password" placeholder="密码"/>
                        <input type="password" placeholder="确认密码"/>
                        <button onClick={this.handleClick.bind(this)}>注册</button>
                        <p className="message">如果已注册?<Link to="/login">登陆</Link></p>
                    </form>
                </div>
            </div>
        )
    }
}