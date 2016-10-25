import './css/style';

import React from 'react';
import ReactDOM from 'react-dom';
import reqwest from 'reqwest';
import Rx from 'Rxjs/Rx';
import Select from 'react-select';
import update from 'react-addons-update';

import 'react-select/dist/react-select.css';

const asOptionList = (namedItems) => namedItems.map(item => ({
  label: item.name,
  value: item.id,
}));

const findValueLabel = (value, options) =>
  options.find(option => option['value'] === value)['label'];

class Form extends React.Component {

  constructor() {
    super();
    this.setGroup = this.setGroup.bind(this);
    this.setPlaylist = this.setPlaylist.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }

  setGroup(group) {
    this.group = {
      id: group,
      name: findValueLabel(group, this.props.groups),
    };
  }

  setPlaylist(playlist) {
    this.playlist = {
      id: playlist,
      name: findValueLabel(playlist, this.props.playlists),
    };
  }

  onSubmit(event) {
    event.preventDefault();
    this.props.onSubmit(this.group, this.playlist);
  }

  render() {
    return (
      <form className="form-horizontal">
        <div className="form-group">
          <div className="col-sm-6">
            <Select
              name="group_id"
              autoblur
              options={this.props.groups}
              placeholder="Search for group"
              scrollMenuIntoView={false}
              onChange={this.setGroup}
            />
          </div>
          <div className="col-sm-6">
            <Select
              name="playlist_id"
              autoblur
              options={this.props.playlists}
              placeholder="Search for playlist"
              scrollMenuIntoView={false}
              onChange={this.setPlaylist}
            />
          </div>
        </div>
        <button
          onClick={this.onSubmit}
          disabled={!this.props.submitEnabled}
          className="btn btn-default"
          type="submit">
          Go!
        </button>
      </form>
    );
  }
}

Form.propTypes = {
  groups: React.PropTypes.arrayOf(
    React.PropTypes.objectOf(React.PropTypes.string)).isRequired,
  onSubmit: React.PropTypes.func.isRequired,
  playlists: React.PropTypes.arrayOf(
    React.PropTypes.objectOf(React.PropTypes.string)).isRequired,
  submitEnabled: React.PropTypes.bool.isRequired,
};

const ProgressIndicator = props => (
  <div>
    <h1>
      {props.groupName} ➞ {props.playlistName}: {`${props.progress} %`}
      {props.progress === 100 ? '✔' : ''}
    </h1>
    {props.progress !== 100
      ? <hr style={{
        width: `${props.progress}%`,
        height: '5px',
        color: '#16a085',
        backgroundColor: '#16a085',
      }}
      /> : ''}
  </div>
);

ProgressIndicator.propTypes = {
  groupName: React.PropTypes.string.isRequired,
  playlistName: React.PropTypes.string.isRequired,
  progress: React.PropTypes.number.isRequired,
};

class RootComponent extends React.Component {
  constructor() {
    super();
    this.playlists = [];
    this.groups = [];
    this.state = {
      playlists: this.playlists,
      groups: this.groups,
    };
    this.onSubmit = this.onSubmit.bind(this);
  }

  componentWillMount() {
    const data = JSON.parse(
      document.getElementsByTagName('body')[0].dataset.page);
    this.playlists = data['youtube_playlists'];
    this.groups = data['facebook_groups'];
    this.updateUrl = data['update_url'];
    this.setState({
      jobs: [],
      playlists: asOptionList(this.playlists),
      groups: asOptionList(this.groups),
      submitEnabled: true,
    });
  }

  onSubmit(group, playlist) {
    const jobIndex = this.state.jobs.length;
    this.setState({
      jobs: update(
        this.state.jobs,
        {
          $push: [{
            progress: 0,
            groupName: group.name,
            playlistName: playlist.name,
          }],
        }),
      submitEnabled: false,
    });
    reqwest({
      url: this.updateUrl,
      data: JSON.stringify({ group_id: group.id, playlist_id: playlist.id }),
      method: 'post',
      contentType: 'application/json',
    })
    .then(this.monitorProgress.bind(
      this, group.name, playlist.name, jobIndex));
  }

  monitorProgress(groupName, playlistName, jobIndex, data) {
    this.setState({
      submitEnabled: true,
    });
    const doneUrl = data.done_url;
    Rx.Observable
      .interval(1000)
      .switchMap(() => Rx.Observable.fromPromise(
        reqwest({url: doneUrl}).then(data => Number(data['progress']))))
      .takeWhile(progress => progress !== 100)
      .concat(Rx.Observable.just(100))
      .subscribe(
        progress => this.setState({
          jobs: update(
            this.state.jobs,
            {
              [jobIndex]: {
                progress: {
                  $set: progress,
                },
              },
            }),
        }));
  }

  render() {
    return (
      <div>
        <Form
          groups={this.state.groups}
          playlists={this.state.playlists}
          submitEnabled={this.state.submitEnabled}
          onSubmit={this.onSubmit}
        />
        {this.state.jobs.map((job, i) =>
          <ProgressIndicator
            key={i}
            groupName={job.groupName}
            playlistName={job.playlistName}
            progress={job.progress}
          />)
        }
      </div>
    );
  }
}

ReactDOM.render(<RootComponent />, document.getElementById('app'));
