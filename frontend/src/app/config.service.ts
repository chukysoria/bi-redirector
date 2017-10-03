import { Injectable } from '@angular/core';
import { Config } from './config';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

@Injectable()
export class ConfigService {

  private configURL = 'http://localhost:5000/api/configs';

  constructor(private http: Http) { }

  getConfigs(): Promise<Config[]> {
    return this.http
      .get(this.configURL)
      .toPromise()
      .then(response => response.json().data as Config[])
      .catch(this.handleError);
  }

  handleError(error: any): Promise<any> {
    console.error('An error occurred', error); // for demo purposes only
    return Promise.reject(error.message || error);
  }

}
