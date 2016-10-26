import './css/style';

import React from 'react';
import ReactDOM from 'react-dom';
import reqwest from 'reqwest';
import Rx from 'rxjs/Rx';
import Select from 'react-select';
import update from 'react-addons-update';

import 'react-select/dist/react-select.css';

const asOptionList = (namedItems) => namedItems.map(item => ({
  label: item.name,
  value: item.id,
}));

const findValueLabel = (value, options) =>
  options.find(option => option['value'] === value)['label'];

class StableSelect extends React.Component {
  shouldComponentUpdate() {
    return !this.refs.select.props.options;
  }

  render() {
    return <Select ref="select" {...this.props} />;
  }
}

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
            <StableSelect
              autoblur
              options={this.props.groups}
              placeholder="Search for group"
              scrollMenuIntoView={false}
              onChange={this.setGroup}
            />
          </div>
          <div className="col-sm-6">
            <StableSelect
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
    <h5>
      {props.groupName} ➞ {props.playlistName}&nbsp;
      {props.message ? `★ ${props.message}` : ''}&nbsp;
      {props.progress === 100 ? '✔' : `${props.progress} %`}
    </h5>
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
  message: React.PropTypes.string.isRequired,
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
    this.playlists = asOptionList(data['youtube_playlists']);
    this.groups = asOptionList(data['facebook_groups']);
    this.updateUrl = data['update_url'];
    this.setState({
      jobs: [],
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
            progress: {
              facebookProgress: 0,
              youtubeProgress: 0,
            },
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
        reqwest({url: doneUrl}).then(data => ({
          facebookProgress: Number(data['facebook_progress']),
          youtubeProgress: Number(data['youtube_progress']),
        }))))
      .takeWhile(progress => progress['youtubeProgress'] !== 100)
      .concat(Rx.Observable.of({ youtubeProgress: 100, facebookProgress: 100 }))
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
          groups={this.groups}
          playlists={this.playlists}
          submitEnabled={this.state.submitEnabled}
          onSubmit={this.onSubmit}
        />
        {this.state.jobs.map((job, i) => {
          let progress, message;
          if (job.progress.facebookProgress === 100) {
            progress = job.progress.youtubeProgress;
            if (job.progress.youtubeProgress < 100) {
              message = 'Uploading videos to YouTube...';
            }
          } else {
            progress = job.progress.facebookProgress;
            message = 'Getting videos from Facebook...';
          }
          return (<ProgressIndicator
            key={i}
            groupName={job.groupName}
            playlistName={job.playlistName}
            progress={progress}
            message={message}
          />);
        })}
      </div>
    );
  }
}

ReactDOM.render(<RootComponent />, document.getElementById('app'));
