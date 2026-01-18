import React from 'react';
import '../App.css';

class FeedPage extends React.Component {
    feed = [{ "matchId": 1, "name": "Tournament 1" },
            { "matchId": 2, "name": "Tournament 2" },
            { "matchId": 3, "name": "Tournament 3" },
            { "matchId": 4, "name": "Tournament 4" },
            { "matchId": 5, "name": "Tournament 5" }];
    /*constructor(props) {
        super(props);
        let xhr = new XMLHttpRequest();
        xhr.open('GET', 'http://176.118.165.63:6670/albums', false);
        try {
            xhr.send();
            if (xhr.status !== 200) {
                alert(`Error ${xhr.status}: ${xhr.statusText}`);
            } else {
                this.feed = xhr.response;
                //alert(JSON.parse(this.resp)[0]["name"]);
            }
        } catch (err) {
            alert("Request failed");
        }
        for (let i = 0; i < 6; ++i) {
            xhr.open('GET', 'http://176.118.165.63:6670/albums/' + (i + 7) + '/works', false);
            try {
                xhr.send();
                if (xhr.status !== 200) {
                    alert(`Error ${xhr.status}: ${xhr.statusText}`);
                } else {
                    this.works.push(xhr.response);
                    //alert(JSON.parse(this.works[i])[0]["image"]["data"]);
                }
            } catch (err) {
                alert("Request failed " + err);
            }
        }
    }*/

    render() {
        return (
            <div>
                <div className='Header-box'>
                    Tennis Result Validator
                    <div id='links' style={{ position: 'fixed', right: '55px', top: '20px' }}>
                        <a href='profile' style={{ color: '#FFFFFF'}}>
                            Anna Petrova
                        </a>
                    </div>
                    <div id='profile_icon' style={{position: 'fixed', right: '15px', top: '20px'}}></div>
                </div>

                <link href="dist/smooth-scrollbar.css" rel="stylesheet" />
                <script src="dist/smooth-scrollbar.js"></script>
                <section scrollbar>
                    <div>
                        {/*JSON.parse(this.feed).map(album => {
                            return (
                                <a href={"albums/" + album["albumId"]} className='Feed-item' key={album["albumId"]}>
                                    <p className='Center-img'><img className='Feed-item__img' src={"data:image/jpg;base64," +
                                        JSON.parse(this.works[0])[0]["image"]["data"]}
                                        alt={album["name"]}></img></p>
                                    <div className='Feed-item__title'>
                                        {album["name"]}
                                    </div>
                                </a>
                            );
                        })*/
                        this.feed.map(match => {
                            return (
                                <a href={"matches/" + match["matchId"]} className='Feed-item' key={match["matchId"]}>
                                    <div className='Feed-item__title'>
                                        {match["name"]}
                                    </div>
                                </a>
                            );
                        })}
                    </div>
                </section>
            </div>
        )
    }
}

export default FeedPage;