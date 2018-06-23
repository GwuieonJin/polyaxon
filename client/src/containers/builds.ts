import { connect, Dispatch } from 'react-redux';

import { AppState } from '../constants/types';
import Builds from '../components/builds';
import { BuildModel } from '../models/build';

import * as actions from '../actions/build';
import { getOffset } from '../constants/paginate';

export function mapStateToProps(state: AppState, params: any) {
  let useFilter = () => {
    let builds: BuildModel[] = [];
    let project = state.projects.byUniqueNames[params.projectName];
    let BuildNames = project.builds;
    BuildNames.forEach(
      function (build: string, idx: number) {
        builds.push(state.builds.byUniqueNames[build]);
      });
    return {builds: builds, count: project.num_builds};
  };

  let useLastFetched = () => {
    let buildNames = state.builds.lastFetched.names;
    let count = state.builds.lastFetched.count;
    let builds: BuildModel[] = [];
    buildNames.forEach(
      function (build: string, idx: number) {
        builds.push(state.builds.byUniqueNames[build]);
      });
    return {builds: builds, count: count};
  };
  let results = useLastFetched();

  return {
    isCurrentUser: state.auth.user === params.user,
    builds: results.builds,
    count: results.count
  };
}

export interface DispatchProps {
  onCreate?: (build: BuildModel) => actions.BuildAction;
  onDelete?: (build: BuildModel) => actions.BuildAction;
  onUpdate?: (build: BuildModel) => actions.BuildAction;
  fetchData?: (currentPage?: number, query?: string, sort?: string) => actions.BuildAction;
}

export function mapDispatchToProps(dispatch: Dispatch<actions.BuildAction>, params: any): DispatchProps {
  return {
    onCreate: (build: BuildModel) => dispatch(actions.createBuildActionCreator(build)),
    onDelete: (build: BuildModel) => dispatch(actions.deleteBuildActionCreator(build)),
    onUpdate: (build: BuildModel) => dispatch(actions.updateBuildActionCreator(build)),
    fetchData: (currentPage?: number, query?: string, sort?: string) => {
      let filters: {[key: string]: number|boolean|string} = {};
      if (query) {
        filters.query = query;
      }
      if (sort) {
        filters.sort = sort;
      }
      let offset = getOffset(currentPage);
      if (offset != null) {
        filters.offset = offset;
      }
      return dispatch(actions.fetchBuilds(params.projectName, filters));
    }
  };
}

export default connect(mapStateToProps, mapDispatchToProps)(Builds);