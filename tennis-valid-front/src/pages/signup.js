import React from 'react';
import '../App.css';
import { Link } from "react-router-dom";

class SignupPage extends React.Component {
    async sendSignUpData(data) {
        /*return await fetch('http://176.118.165.63:6670/users/login', {
            method: 'POST',
            body: data,
        })*/
    }

    async handleSignUpForm(event) {
        event.preventDefault()
        const data = new FormData(event.target)
        const response = await this.sendSignUpData(data)
        if (response.status === 200) {
            //const body = await response.json()
            //alert("Успешная Регистрация:\nТокен:" + body["token"])
        }
        else alert(response.status)
    }

    render() {
        return (
            <div>
                <div className='Header-box'>
                    Tennis Result Validator
                </div>

                <form action="" id="register">
                    <center>
                        <input type="text" id="name" name="name" placeholder="Name" className="Text-input"/>
                    </center>
                    <center>
                        <input type="text" id="surname" name="surname" placeholder="Surname" className="Text-input"/>
                    </center>
                    <center>
                        <input type="email" id="email" name="mail" placeholder="Email" className="Text-input"/>
                    </center>
                    <center>
                        <input type="password" id="pass" name="password" placeholder="Password" className="Text-input"/>
                    </center>
                    <center>
                        <input type="password" id="pass" name="password" placeholder="Confirm password" className="Text-input"/>
                    </center>
                    <center>
                        <label className="Label-font">
                            <input type="checkbox" name="isOrganizer" className="Checkbox"/> I'm an organizer
                        </label>
                    </center>
                    <center>
                        <Link to='/feed'>
                            <button type="submit" className="Btn" onSubmit={this.handleSignUpForm}>
                                Register
                            </button>
                        </Link>
                    </center>
                </form>
                <center>
                    <a href="/login" className="Label-font">
                        I already have an account
                    </a>
                </center>
            </div>
        )
    }
}

export default SignupPage;