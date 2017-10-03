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

  constructor(private configService: ConfigService) { }

  ngOnInit() {
    this.configService.getConfigs().then(configs => this.configs = configs);
  }

}
