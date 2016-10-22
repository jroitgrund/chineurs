import './css/style';

// require("babel/polyfill");

import React from 'react';
import ReactDOM from 'react-dom';
import Select from 'react-select';

import 'react-select/dist/react-select.css';

const asOptionList = (namedItems) => namedItems.map(item => ({
  label: item.name,
  value: item.id,
}));

class RootComponent extends React.Component {
  constructor() {
    super();
    this.playlists = [];
    this.groups = [];
    this.state = {
      playlists: this.playlists,
      groups: this.groups,
    };
  }

  componentWillMount() {
    const data = JSON.parse(
      document.getElementsByTagName('body')[0].dataset.page);
    this.playlists = data['youtube_playlists'];
    this.groups = data['facebook_groups'];
    this.updateUrl = data['update_url'];
    this.setState({
      playlists: asOptionList(this.playlists),
      groups: asOptionList(this.groups),
      updateUrl: this.updateUrl,
    });
  }

  render() {
    return (
      <div>
        <form
          className="form-horizontal"
          method="get"
          action={this.state.updateUrl}>
          <div className="form-group">
            <div className="col-sm-6">
              <Select
                name="group_id"
                autoblur
                options={this.state.groups}
                onInputChange={this.onGroupQuery}
                placeholder="Search for group"
                scrollMenuIntoView={false}
              />
            </div>
            <div className="col-sm-6">
              <Select
                name="playlist_id"
                autoblur
                options={this.state.playlists}
                onInputChange={this.onPlaylistQuery}
                placeholder="Search for playlist"
                scrollMenuIntoView={false}
              />
            </div>
          </div>
          <button
            className="btn btn-default"
            type="submit">Go!</button>
        </form>
      </div>
    );
  }
}

ReactDOM.render(<RootComponent />, document.getElementById('app'));
