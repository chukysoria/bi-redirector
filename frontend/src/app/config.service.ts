import { Injectable } from '@angular/core';
import { Config } from './config';
import { Headers, Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

@Injectable()
export class ConfigService {

  private configURL = '/api/configs';

  constructor(private http: Http) { }

  create(name: string, value: string): Promise<Config> {
    return this.http
      .post(this.configURL, JSON.stringify({name: name, value: value}), {headers: this.headers()})
      .toPromise()
      .then(response => response.json().data as Config)
      .catch((err) => this.handleError(err));
  }

  getConfigs(): Promise<Config[]> {
    return this.http
      .get(this.configURL)
      .toPromise()
      .then(response => response.json().data as Config[])
      .catch((err) => this.handleError(err));
  }

  update(config: Config): Promise<Config> {
    const url = `${this.configURL}/${config.id}`;
    return this.http
      .put(url, JSON.stringify(config), {headers: this.headers()})
      .toPromise()
      .then(response => response.json().data as Config)
      .catch((err) => this.handleError(err));
  }

  delete(id: number): Promise<void> {
    const url = `${this.configURL}/${id}`;
    return this.http
      .delete(url)
      .toPromise()
      .then(() => null)
      .catch ((err) => this.handleError(err));
  }

  private headers(): Headers {
    return new Headers({'Content-Type': 'application/json'});
  }

  private handleError(error: any): Promise<any> {
    console.error('An error occurred', error); // for demo purposes only
    return Promise.reject(error.message || error);
  }

}
