import { TestBed } from '@angular/core/testing';

import { Carta } from './carta';

describe('Carta', () => {
  let service: Carta;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Carta);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
