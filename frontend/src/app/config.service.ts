import { Injectable } from '@angular/core';
import { Config } from './config';
import { AuthHttp } from 'angular2-jwt';

import 'rxjs/add/operator/toPromise';

@Injectable()
export class ConfigService {

  private configURL = '/api/configs';

  constructor(private authHttp: AuthHttp) { }

  create(name: string, value: string): Promise<Config> {
    return this.authHttp
      .post(this.configURL, JSON.stringify({name: name, value: value}))
      .toPromise()
      .then(response => response.json().data as Config)
      .catch((err) => this.handleError(err));
  }

  getConfigs(): Promise<Config[]> {
    return this.authHttp
      .get(this.configURL)
      .toPromise()
      .then(response => response.json().data as Config[])
      .catch((err) => this.handleError(err));
  }

  update(config: Config): Promise<Config> {
    const url = `${this.configURL}/${config.name}`;
    return this.authHttp
      .put(url, JSON.stringify(config))
      .toPromise()
      .then(response => response.json().data as Config)
      .catch((err) => this.handleError(err));
  }

  delete(name: string): Promise<void> {
    const url = `${this.configURL}/${name}`;
    return this.authHttp
      .delete(url)
      .toPromise()
      .then(() => null)
      .catch ((err) => this.handleError(err));
  }

  private handleError(error: any): Promise<any> {
    console.error('An error occurred', error); // for demo purposes only
    return Promise.reject(error.message || error);
  }

}
