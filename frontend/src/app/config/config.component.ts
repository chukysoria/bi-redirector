import { AuthService } from './../auth.service';
import { Component, OnInit } from '@angular/core';
import { Config } from '../config';
import { ConfigService } from '../config.service';

@Component({
  selector: 'app-config',
  templateUrl: './config.component.html',
  styleUrls: ['./config.component.css']
})
export class ConfigComponent implements OnInit {

  public configs: Config[];

  constructor(private configService: ConfigService, public auth: AuthService) { }

  ngOnInit() {
    this.getConfigs();
  }

  getConfigs(): void {
    this.configService.getConfigs().then(configs => this.configs = configs.sort((a, b) => {
      if (a.name < b.name) {return -1; }
      if (a.name > b.name) {return 1; }
      return 0;
    }));
  }

  add(name: string, value: string, secure: boolean): void {
    name = name.trim();
    if (!name) { return; }
    this.configService.create(name, value, secure)
      .then(config => {
        this.configs.push(config);
      });
  }

  update(config: Config): void {
    this.configService.update(config)
      .then(newConfig => {
        const index = this.configs.findIndex(c => c.name === newConfig.name);
        this.configs[index] = newConfig;
      });
  }

  delete(config: Config): void {
    this.configService.delete(config.name)
      .then(() => this.configs = this.configs.filter(c => c !== config)
      );
  }

}
