import React from 'react';
import '../App.css';
import { Link } from "react-router-dom";

class LoginPage extends React.Component {
    async handleLogInForm(event) {
        //event.preventDefault()
        //const data = new FormData(event.target)
        //const response = await this.sendLogInData(data)
        //if (response.status === 200) {
        //    const body = await response.json()
        //    alert("Успешная регистрация:\nТокен:" + body["token"])
        //}
        //else alert(response.status)
    }

    render() {
        return (
            <div>
                <div className='Header-box'>
                    Tennis Result Validator
                </div>

                <form action="" id="sign_in">
                    <center>
                        <input type="email" id="email" name="mail" placeholder="Email" className="Text-input"/>
                    </center>
                    <center>
                        <input type="password" id="pass" name="password" placeholder="Password" className="Text-input"/>
                    </center>
                    <center>
                        <Link to='/feed'>
                            <button type="submit" className="Btn" onSubmit={this.handleLogInForm}>
                                Log in
                            </button>
                        </Link>
                    </center>
                </form>
                <center>
                    <a href="/signup" className="Label-font">
                        I don't have an account
                    </a>
                </center>
            </div>
        )
    }
}

export default LoginPage;