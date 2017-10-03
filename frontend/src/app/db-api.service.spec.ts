import { TestBed, inject } from '@angular/core/testing';

import { DbApiService } from './db-api.service';

describe('DbApiService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [DbApiService]
    });
  });

  it('should be created', inject([DbApiService], (service: DbApiService) => {
    expect(service).toBeTruthy();
  }));
});
