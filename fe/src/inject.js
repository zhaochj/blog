import React from 'react';

//变形一， 目的是对_Login组件进行包装，注入props属性，_Login = inject(_Login)
// function inject(Com) {
//     return(class Login extends React.Component {
//         render() {
//             return <Com service={userService} />;
//         }
//     })
//
// };

// 变形二,改写成一个匿名函数
// const inject = Com => {
//     return(class extends React.Component {
//         render() {
//             return <Com service={userService} />;
//         }
//     })
//
// };

// 变形三，进一步变化
// const inject = Com => class extends React.Component {
//         render() {
//             return <Com service={userService} />;
//         }
//     };

// 变形四，修改为无状态组件
// const inject = Com => props => (
//     <Com service={userService} />
// );

// 变形五，将属性值为作为参数传递
// const inject = (service, Com) => props => (
//     <Com service={service} />
// );

//变形六，进行一步柯里化
// const inject = service => Com => props => <Com service={service} />

// 变形七，属性改造，service变量命名不通用，改造成对象
const inject = obj => Com => props => <Com {...obj} {...props}/>;  // 无状态组件需要在Com组件中把props自身也要注入
export default inject;